from typing import Any

from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.route("/")
def index() -> Any:
    return render_template("pages/home.jinja2")


@bp.route("/hotel")
def hotel() -> Any:
    return render_template("pages/hotel.jinja2")


@bp.route("/events")
def events() -> Any:
    return render_template("pages/events.jinja2")


@bp.route("/registry")
def registry() -> Any:
    return render_template("pages/registry.jinja2")


@bp.route("/faq", methods=["GET"])
def faq() -> Any:
    return render_template("pages/faq.jinja2")
