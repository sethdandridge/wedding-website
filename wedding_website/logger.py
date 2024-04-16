import logging
import sys
import time
import uuid

import structlog
from flask import Flask, Response, request, session
from structlog.typing import FilteringBoundLogger


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
        structlog.processors.TimeStamper(fmt="iso"),
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
        processors.append(structlog.dev.ConsoleRenderer(sort_keys=False))
    else:
        # Print JSON when we run, e.g., in a Docker container.
        processors.append(structlog.processors.JSONRenderer(sort_keys=False))
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger: FilteringBoundLogger = structlog.get_logger()

    # Middleware to generate a request ID and bind it to log entries
    @app.before_request
    def before_request() -> None:
        request.t0 = time.time()
        structlog.contextvars.bind_contextvars(
            correlation_id=str(uuid.uuid4()),
            method=request.method,
            path=request.path,
            body=request.get_data(as_text=True),
            ip=request.remote_addr,
        )
        logger.info("Request received", cookies=dict(session))

    @app.after_request
    def after_request(response: Response) -> Response:
        response_time_ms = int((time.time() - request.t0) * 1000)
        logger.info(
            "Request completed",
            status=response.status_code,
            set_cookies=dict(session),
            response_time_ms=response_time_ms,
        )
        structlog.contextvars.clear_contextvars()
        return response


def get_logger() -> FilteringBoundLogger:
    return structlog.get_logger()
