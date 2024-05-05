import sqlite3
from contextlib import closing

import qrcode
from PIL import Image

LIGHT_LAVENDER_BLUE = "#d6d7ed"

with closing(sqlite3.connect("../../instance/wedding_website.sqlite")) as conn:
    with closing(conn.cursor()) as c:
        c.execute("SELECT id, cute_name FROM household;")
        households = c.fetchall()

logo = Image.open("dogsie.png").convert("RGBA")
# Resize logo to fit into the QR code
logo_size = 264  # Adjust logo size here
logo = logo.resize((logo_size, logo_size), Image.Resampling.NEAREST)

for household in households:
    household_id = household[0]
    cute_name = household[1]
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=24,
        border=0,
    )
    url = f"https://seth.and.sydney/rsvp/{cute_name}"
    qr.add_data(url)
    qr.make(fit=True)
    print(household_id, url)

    # Create QR code image with a transparent background
    img = qr.make_image(fill_color=LIGHT_LAVENDER_BLUE, back_color="transparent").convert("RGBA")

    # Calculate dimensions for logo box
    logo_box = (
        (img.size[0] - logo_size) // 2,
        (img.size[1] - logo_size) // 2,
        (img.size[0] + logo_size) // 2,
        (img.size[1] + logo_size) // 2,
    )

    # Create a transparent patch the size of the logo
    transparent_patch = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 0))

    # Clear the area on the QR code where the logo will be placed
    img.paste(transparent_patch, (logo_box[0], logo_box[1]))

    # Add logo over the transparent area
    img.paste(logo, (logo_box[0], logo_box[1]), logo)

    # Save the modified QR code
    img.save(f"codes/{household_id}.png")
