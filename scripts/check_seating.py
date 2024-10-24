import sqlite3
from contextlib import closing

guests = set()
with open("instance/seating_guests.txt") as f:
    for guest in f:
        guests.add(guest.strip())
print(len(guests))

with closing(sqlite3.connect("instance/wedding_website_final.sqlite")) as conn:
    with closing(conn.cursor()) as c:
        c.execute("SELECT name FROM guest WHERE wedding_response = 1;")
        results = c.fetchall()
        guests_website = set(r[0] for r in results)

# Print guests that are in the seating list but not in the website list
print("Guests in seating list but not in website list:")
for guest in guests - guests_website:
    print(guest)

print("Guests in website list but not in seating list:")
for guest in guests_website:
    if guest not in guests:
        print(guest)
