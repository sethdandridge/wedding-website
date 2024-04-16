import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any

from flask import Flask, make_response, request, send_from_directory
from flask.logging import default_handler

from wedding_website import db, pages, rsvp


def create_app(testing: bool = False) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config["SECRET_KEY"] = "INSECURE"
    app.config["SERVER_NAME"] = "seth.and.sydney:5000"
    app.config["DATABASE"] = os.path.join(app.instance_path, "wedding_website.sqlite")

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # logging stuff
    app.logger.removeHandler(default_handler)

    class RequestFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            record.path = request.path
            record.remote_addr = request.remote_addr
            return super().format(record)

    formatter = RequestFormatter("[%(asctime)s] %(remote_addr)s %(path)s %(levelname)s %(module)s %(message)s")
    rotating_file_handler = RotatingFileHandler(
        app.instance_path + "/log.txt", maxBytes=1000 * 1000 * 10, backupCount=10  # 10 megabytes
    )
    rotating_file_handler.setFormatter(formatter)
    if testing is False:
        app.logger.addHandler(rotating_file_handler)

    # Create the database
    db.init_db(app)

    @app.route("/favicon.ico")
    def favicon() -> Any:
        return send_from_directory("favicons", "favicon.ico", mimetype="image/vnd.microsoft.icon")

    @app.route("/static/<path:filename>")
    def custom_static(filename: str) -> Any:
        response = make_response(send_from_directory("static", filename))
        response.cache_control.max_age = 60 * 60  # 1 hour
        response.cache_control.no_cache = None
        return response

    # heartbeat route for testing
    @app.route("/heartbeat")
    def heartbeat() -> Any:
        return "200 OK"

    app.register_blueprint(pages.bp)

    app.register_blueprint(rsvp.bp)

    return app
