import csv
import sqlite3
from contextlib import closing

with open("instance/guests.csv") as f:
    reader = csv.DictReader(f)
    guests = list(reader)

with closing(sqlite3.connect("instance/wedding_website.sqlite")) as conn:
    with closing(conn.cursor()) as c:
        for guest in guests:
            if guest["ID"] == "":
                continue
            if guest["Household ID"] == "":
                continue
            guest_id = int(guest["ID"])
            household_id = int(guest["Household ID"])
            is_plus_one = guest["First Name"] == "Guest"
            if is_plus_one is True:
                name = None
                aliases = []
            else:
                name = f"{guest['First Name']} {guest['Last Name']}"
                aliases = [g.lower() for g in guest["Aliases Lower"].split(",")]
            try:
                c.execute(
                    "INSERT INTO guest (id, household_id, name, is_plus_one) VALUES (?, ?, ?, ?)",
                    (guest_id, household_id, name, is_plus_one),
                )
            except sqlite3.IntegrityError:
                print(f"Guest {name} {guest_id} already exists in the database")
            for alias in aliases:
                try:
                    c.execute(
                        "INSERT INTO guest_to_alias (guest_id, alias) VALUES (?, ?)",
                        (guest_id, alias.strip()),
                    )
                except sqlite3.IntegrityError:
                    print(f"Alias {alias} already exists in the database")
        conn.commit()
