import qrcode
from PIL import Image

LIGHT_LAVENDER_BLUE = "#d6d7ed"


logo = Image.open("scripts/qr_codes/dogsie.png").convert("RGBA")
# Resize logo to fit into the QR code
logo_size = 264  # Adjust logo size here
logo = logo.resize((logo_size, logo_size), Image.Resampling.NEAREST)

qr = qrcode.QRCode(
    version=6,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=24,
    border=0,
)
url = "https://seth.and.sydney/rsvp"
qr.add_data(url)
qr.make(fit=True)

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
img.save("scripts/qr_codes/codes/generic.png")
