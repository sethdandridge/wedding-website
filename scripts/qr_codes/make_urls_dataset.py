import sqlite3
from contextlib import closing

with closing(sqlite3.connect("instance/wedding_website.sqlite")) as conn:
    with closing(conn.cursor()) as c:
        c.execute("SELECT id, cute_name FROM household;")
        households = c.fetchall()

with open("instance/urls.txt", "w") as f:
    line = "ID\tQRCode\tURL\n"
    f.write(line)
    for household in households:
        household_id = household[0]
        cute_name = household[1]
        url = f"https://seth.and.sydney/rsvp/{cute_name}"
        qrcode = f"/Volumes/code/wedding-website/scripts/qr_codes/codes/{household_id}.png"
        line = f"{household_id}\t{qrcode}\t{url}\n"
        f.write(line)
