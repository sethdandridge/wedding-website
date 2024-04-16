from typing import Any, Union

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, session, url_for

from wedding_website.exceptions import GuestNotFoundError
from wedding_website.models.guest import Guest
from wedding_website.models.household import Household

bp = Blueprint("rsvp", __name__)


def _get_guests() -> list[Guest]:
    session_guests = session["guests"]
    guests = [Guest(**sg) for sg in session_guests]
    return guests


def _persist_guests(guests: list[Guest]) -> None:
    for guest in guests:
        guest.save()


@bp.route("/", subdomain="<household_cute_subdomain>")
def rsvp_redirect(household_cute_subdomain: str) -> Response:
    household_cute_subdomain = household_cute_subdomain.rstrip(".and")
    household_cute_key = household_cute_subdomain.replace(".", "-")
    current_app.logger.info(f"household_cute_key: {household_cute_key}")
    return redirect(f"//{current_app.config['SERVER_NAME']}/rsvp/{household_cute_key}/ceremony", code=302)


@bp.route("/rsvp")
def get_rsvp() -> Any:
    return render_template("pages/rsvp.jinja2")


@bp.route("/rsvp", methods=["POST"])
def post_rsvp() -> Any:
    name = request.form.get("name")
    if "initial_lookup" in session:
        print(session["initial_lookup"], "looked up name", name)
    if not name:
        flash("Please enter your name.")
        return render_template("pages/rsvp.jinja2")
    try:
        name = name.strip().lower()
        guest = Guest.from_alias(name)
    except GuestNotFoundError:
        flash(f"Could not find {name} in the guest list. Please try again.")  # Todo: add help
        return render_template("pages/rsvp.jinja2")
    return render_template(
        "pages/rsvp_name_confirmation.jinja2",
        url=f"//{guest.household.cute_subdomain}.and.{current_app.config['SERVER_NAME']}",
        guest_name=guest.name,
    )


@bp.route("/rsvp/<household_cute_name>/ceremony")
def get_rsvp_form_ceremony(household_cute_name: str) -> Any:
    if "initial_lookup" not in session:
        session["initial_lookup"] = household_cute_name
    household = Household.from_cute_name(household_cute_name)
    guests = household.guests
    session["guests"] = guests
    return render_template("pages/rsvp_form.jinja2", guests=guests)


@bp.route("/rsvp/<household_cute_name>/ceremony", methods=["POST"])
def post_rsvp_form_ceremony(household_cute_name: str) -> Union[Response, str]:
    household = Household.from_cute_name(household_cute_name)
    guests = _get_guests()
    for i, guest in enumerate(guests, start=1):
        guest.wedding_response = request.form.get(f"guest-{i}") == "yes"
        if guest.is_plus_one:
            guest.name = request.form.get(f"guest-{i}-name")
        # If a plus-one is not coming to the ceremony, they are not coming to the dinner or brunch
        if guest.is_plus_one and not guest.wedding_response:
            guest.dinner_response = False
            guest.brunch_response = False
    session["guests"] = guests
    is_anyone_coming = any(guest.wedding_response for guest in guests)
    if is_anyone_coming is False:
        _persist_guests(guests)
        session["is_coming"] = False
        return redirect(url_for("rsvp.get_rsvp_confirmation"), code=302)  # No one is coming
    else:
        session["is_coming"] = True
        if household.is_invited_dinner:
            return redirect(url_for("rsvp.get_rsvp_form_dinner", household_cute_name=household_cute_name), code=302)
        else:
            return redirect(url_for("rsvp.get_rsvp_form_brunch", household_cute_name=household_cute_name), code=302)


@bp.route("/rsvp/<household_cute_name>/dinner")
def get_rsvp_form_dinner(household_cute_name: str) -> Any:
    guests = _get_guests()
    indexed_guests = [g for g in guests if g.wedding_response or not g.is_plus_one]
    return render_template("pages/rsvp_form_dinner.jinja2", guests=indexed_guests)


@bp.route("/rsvp/<household_cute_name>/dinner", methods=["POST"])
def post_rsvp_form_dinner(household_cute_name: str) -> Response:
    guests = _get_guests()
    indexed_guests = guests = [g for g in guests if g.wedding_response or not g.is_plus_one]
    for i, guest in enumerate(indexed_guests, start=1):
        guest.dinner_response = request.form.get(f"guest-{i}") == "yes"
    session["guests"] = guests
    return redirect(url_for("rsvp.get_rsvp_form_brunch", household_cute_name=household_cute_name), code=302)


@bp.route("/rsvp/<household_cute_name>/brunch")
def get_rsvp_form_brunch(household_cute_name: str) -> Any:
    guests = _get_guests()
    guests = [g for g in guests if not (not g.wedding_response and g.is_plus_one)]
    return render_template("pages/rsvp_form_brunch.jinja2", guests=guests)


@bp.route("/rsvp/<household_cute_name>/brunch", methods=["POST"])
def post_rsvp_form_brunch(household_cute_name: str) -> Response:
    guests = _get_guests()
    indexed_guests = [g for g in guests if not (not g.wedding_response and g.is_plus_one)]
    for i, guest in enumerate(indexed_guests, start=1):
        guest.brunch_response = request.form.get(f"guest-{i}") == "yes"
    session["guests"] = guests
    _persist_guests(guests)
    return redirect(url_for("rsvp.get_rsvp_confirmation"), code=302)


@bp.route("/rsvp/confirmation")
def get_rsvp_confirmation() -> Any:
    is_coming = bool(session.get("is_coming"))
    return render_template("pages/rsvp_confirmation.jinja2", is_coming=is_coming)
