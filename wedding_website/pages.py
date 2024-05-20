from datetime import date
from typing import Any

from flask import Blueprint, render_template

from wedding_website.client_caching import client_cached

bp = Blueprint("pages", __name__)


@bp.route("/")
@client_cached
def index() -> Any:
    wedding_date = date(2024, 7, 27)
    today = date.today()
    days_until_wedding = (wedding_date - today).days
    return render_template("pages/home.jinja2", days_until_wedding=days_until_wedding)


@bp.route("/hotel")
@client_cached
def hotel() -> Any:
    return render_template("pages/hotel.jinja2")


@bp.route("/events")
@client_cached
def events() -> Any:
    return render_template("pages/events.jinja2")


@bp.route("/registry")
@client_cached
def registry() -> Any:
    return render_template("pages/registry.jinja2")


@bp.route("/faq", methods=["GET"])
@client_cached
def faq() -> Any:
    return render_template("pages/faq.jinja2")
