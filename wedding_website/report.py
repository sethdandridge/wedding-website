from typing import Any

from flask import Blueprint, Response, request, session

from wedding_website.db import get_db_cursor
from wedding_website.models.guest import Guest
from wedding_website.models.household import Household

bp = Blueprint("report", __name__)


def bucket_by_household_id(guest: list[Guest]) -> list[str]:
    guest_buckets: dict[int, list[Guest]] = {}
    for g in guest:
        if g.household.id not in guest_buckets:
            guest_buckets[g.household.id] = []
        guest_buckets[g.household.id].append(g)
    lines = []
    for guests in guest_buckets.values():
        if len(guests) == 1:
            lines.append(guests[0].pretty_name)
        elif len(guests) == 2:
            lines.append(f"{guests[0].pretty_name} & {guests[1].pretty_name}")
        else:
            names = [g.pretty_name for g in guests]
            lines.append(", ".join(names[:-1]) + f" & {names[-1]}")
    return lines


def get_report() -> str:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM guest ORDER BY updated DESC;")
        results = cursor.fetchall()
        cursor.execute("SELECT * FROM household;")
        household_results = cursor.fetchall()
        cursor.execute("SELECT * FROM refresh;")
        refreshes = cursor.fetchone()[0]
        if (
            "is_sydney" in session
            or request.headers.get("X-Forwarded-For", request.remote_addr) == "100.8.244.220"
            or (
                request.headers.get("User-Agent", "")
                == "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1"
                and request.headers.get("X-Forwarded-For", request.remote_addr) == "108.27.236.43"
            )
        ):
            session.permanent = True
            session["is_sydney"] = 1
            refreshes += 1
            cursor.execute("UPDATE refresh SET refreshes = ?;", (refreshes,))
            cursor.connection.commit()
    num_households = len(household_results)
    household_id_to_household = {result[0]: Household(*result) for result in household_results}
    guests = [Guest(*result) for result in results]
    ceremony_yes = []
    ceremony_no = []
    ceremony_none = []
    bagel_brunch_yes = []
    bagel_brunch_no = []
    bagel_brunch_none = []
    dinner_yes = []
    dinner_no = []
    dinner_none = []
    households_responded: set[int] = set()
    for guest in guests:
        if guest.wedding_response == 1:
            households_responded.add(guest.household_id)
            ceremony_yes.append(guest)
        elif guest.wedding_response == 0:
            households_responded.add(guest.household_id)
            ceremony_no.append(guest)
        else:
            ceremony_none.append(guest)

        if guest.brunch_response == 1:
            bagel_brunch_yes.append(guest)
        elif guest.brunch_response == 0:
            bagel_brunch_no.append(guest)
        else:
            bagel_brunch_none.append(guest)
        if household_id_to_household[guest.household_id].is_invited_dinner == 1:
            if guest.dinner_response == 1:
                dinner_yes.append(guest)
            elif guest.dinner_response == 0:
                dinner_no.append(guest)
            else:
                dinner_none.append(guest)
    lines = []
    lines.append("Ceremony:")
    lines.append(" Yes: " + str(len(ceremony_yes)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(ceremony_yes)])
    lines.append(" No: " + str(len(ceremony_no)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(ceremony_no)])
    lines.append(" Remaining: " + str(len(ceremony_none)))
    lines.append("")
    lines.append("Dinner:")
    lines.append(" Yes: " + str(len(dinner_yes)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(dinner_yes)])
    lines.append(" No: " + str(len(dinner_no)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(dinner_no)])
    lines.append(" Remaining: " + str(len(dinner_none)))
    lines.append("")
    lines.append("Bagel Brunch:")
    lines.append(" Yes: " + str(len(bagel_brunch_yes)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(bagel_brunch_yes)])
    lines.append(" No: " + str(len(bagel_brunch_no)))
    lines.extend([f"  {c}" for c in bucket_by_household_id(bagel_brunch_no)])
    lines.append(" Remaining: " + str(len(bagel_brunch_none)))
    lines.append("")
    lines.append(f"Number of households responded: {len(households_responded)}/{num_households}")
    lines.append("")
    lines.append("Number of times Sydney has refreshed this page: " + str(refreshes))
    return "\n".join(lines)


@bp.route("/report/ZtfSdmrSlYcF")
def report() -> Any:
    return Response(response=get_report(), content_type="text/plain")
