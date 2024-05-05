import csv
import sqlite3

with open("instance/households.csv") as f:
    reader = csv.DictReader(f)
    households = list(reader)

conn = sqlite3.connect("instance/wedding_website.sqlite")
c = conn.cursor()
for household in households:
    household_id = int(household["ID"])
    cute_name = household["Hyphen"]
    is_invited_dinner = household["is_invited_dinner"] == "TRUE"
    is_invited_brunch = household["is_invited_brunch"] == "TRUE"
    c.execute(
        "INSERT INTO household (id, cute_name, is_invited_dinner, is_invited_brunch) VALUES (?, ?, ?, ?)",
        (household_id, cute_name, is_invited_dinner, is_invited_brunch),
    )
conn.commit()
conn.close()
