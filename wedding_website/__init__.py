import logging
import os
from typing import Any

from flask import Flask, make_response, send_from_directory
from flask.logging import default_handler

from wedding_website import db, pages, rsvp
from wedding_website.logger import init_logging


def create_app(testing: bool = False) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config["SECRET_KEY"] = "INSECURE"
    app.config["SERVER_NAME"] = "localhost:2700"
    app.config["DATABASE"] = os.path.join(app.instance_path, "wedding_website-test.sqlite")

    # Ignore slashes at the end of URLs
    app.url_map.strict_slashes = False

    # Set up logging
    app.logger.removeHandler(default_handler)
    app.logger.setLevel("WARNING")
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    init_logging(app)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

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
