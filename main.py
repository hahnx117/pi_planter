## Read soil moisture sensor and output soil moisture.

## Import packages

import time
import board
from adafruit_seesaw.seesaw import Seesaw
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import logging
import sys
import datetime

### Setup logging ###
log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s: %(message)s", datefmt="%b %d %Y %H:%M:%S")
handler.setFormatter(formatter)
log.addHandler(handler)

### Configure display ###
## Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

## Define the dimensions of the display
WIDTH = 128
HEIGHT = 64
BORDER = 5

DISPLAY_ADDRESS = 0x3D
SENSOR_ADDRESS = 0x36

try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=DISPLAY_ADDRESS, reset=oled_reset)
except Exception as e:
    logging.info(e)
### Configure soil sensor ###
ss = Seesaw(i2c, addr=SENSOR_ADDRESS)

### Run while loop ###
while True:
    ## Clear display
    oled.fill(0)
    #oled.show()

    ## Setup display
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # Load default font.
    font = ImageFont.load_default(size=16)

    text_string = f"Moisture: {ss.moisture_read()}\nTemp: {ss.get_temp():.1f}"

    logging.info(f"ss.moisture_read: {ss.moisture_read()}")
    logging.info(f"ss.get_temp: {ss.get_temp():.1f}")
    # Draw Some Text
    (font_width, font_height) = font.getbbox(text_string)[2:]

    #draw.multiline_text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2), text_string, font=font, fill=255, align="center")
    draw.multiline_text((0,0), text_string, fill=255, align="center", font_size=18, spacing=16)

    # Display image
    oled.image(image)
    oled.show()
    time.sleep(3)