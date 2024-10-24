import logging
import os
from datetime import timedelta
from typing import Any

from flask import Flask, make_response, send_from_directory
from flask.logging import default_handler
from flask.templating import render_template

from wedding_website import db, pages, report, rsvp
from wedding_website.logger import get_logger, init_logging

logger = get_logger()


def create_app(testing: bool = False) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config["SECRET_KEY"] = "INSECURE"
    app.config["DATABASE"] = os.path.join(app.instance_path, "wedding_website.sqlite")
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)

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

    @app.route("/robots.txt")
    def robots_txt() -> Any:
        return send_from_directory("static", "robots.txt")

    @app.route("/static/<path:filename>")
    def custom_static(filename: str) -> Any:
        response = make_response(send_from_directory("static", filename))
        response.cache_control.max_age = 60 * 60  # 1 hour
        response.cache_control.no_cache = None
        return response

    @app.route("/registry-click")
    def registry_click() -> Any:
        logger.warning("Registry click")
        return "", 204

    @app.errorhandler(404)
    def page_not_found(e: Exception) -> Any:
        return render_template("errors/404.jinja2"), 404

    # heartbeat route for testing
    @app.route("/heartbeat")
    def heartbeat() -> Any:
        return "200 OK"

    app.register_blueprint(pages.bp)

    app.register_blueprint(rsvp.bp)

    app.register_blueprint(report.bp)

    return app
