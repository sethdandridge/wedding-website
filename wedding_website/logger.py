import logging
import sys
import time
import uuid

import structlog
from flask import Flask, Response, request, session
from structlog.typing import FilteringBoundLogger


class CustomConsoleRenderer(structlog.dev.ConsoleRenderer):
    # Define the order of columns here
    KEY_ORDER = (
        "ip",
        "method",
        "url",
        "status",
        "correlation_id",
        "response_time_ms",
        "body",
        "user_agent",
        "cookies",
        "set_cookies",
    )

    def __call__(self, _, __, original_event_dict):  # type: ignore
        new_event_dict = {}
        for key in self.KEY_ORDER:
            if key in original_event_dict:
                new_event_dict[key] = original_event_dict[key]
        for key, value in original_event_dict.items():
            if key not in new_event_dict:
                new_event_dict[key] = value
        return super().__call__(_, __, new_event_dict)


def init_logging(app: Flask) -> None:
    """Initialize logging configuration.

    This function sets up the configuration for the structlog library, which
    is used for structured logging. The configuration includes a list of
    processors that determine how log messages are processed before they are
    written to the log output. The log messages are plain text or JSON depending on
    whether the output is being written to an interactive terminal.
    """
    processors = [
        # Processors that have nothing to do with output,
        # e.g., add timestamps or log level names.
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S"),
    ]
    if app.debug is True:
        processors += [
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
        ]
    if sys.stderr.isatty():
        # Pretty printing when we run in a terminal session.
        # Automatically prints pretty tracebacks when "rich" is installed
        processors.append(CustomConsoleRenderer(sort_keys=False))
    else:
        # Print JSON when we run, e.g., in a Docker container.
        processors.append(structlog.processors.JSONRenderer(sort_keys=False))
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO if app.debug is False else logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger: FilteringBoundLogger = structlog.get_logger()

    # Middleware to generate a request ID and bind it to log entries
    @app.before_request
    def before_request() -> None:
        request.t0 = time.time()
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        structlog.contextvars.bind_contextvars(
            ip=ip,
            method=request.method,
            url=request.headers.get("X-Proxy-Url", request.url),
            user_agent=request.headers.get("User-Agent"),
            correlation_id=str(uuid.uuid4()).split("-")[-1],
        )
        if body := request.get_data(as_text=True):
            if "urlencoded" not in request.headers.get("Content-Type", ""):
                body = "<binary>"
            structlog.contextvars.bind_contextvars(body=body)
        logger.info("Request received", cookies=dict(session))

    @app.after_request
    def after_request(response: Response) -> Response:
        response_time_ms = int((time.time() - request.t0) * 1000)
        logger.log(
            logging.INFO if response.status_code < 400 else logging.ERROR,
            "Request completed" if response.status_code < 400 else "Request errored!",
            set_cookies=dict(session),
            status=response.status_code,
            response_time_ms=response_time_ms,
        )
        structlog.contextvars.clear_contextvars()
        return response


def get_logger() -> FilteringBoundLogger:
    return structlog.get_logger()
