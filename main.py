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
import statistics
import json

def calibrate_soil_sensor(calibrate=False, sensor_object=None):

    default_min = 335
    default_max = 1016
    measured_min = None
    measured_max = None

    if calibrate==True:

        userinput = input("Please put the sensor in dry soil and press ENTER.")

        if userinput is not None:
            i = 0

            reading_list = []

            while i < 20:
                print(sensor_object.moisture_read())
                reading_list.append(sensor_object.moisture_read())


                print(f"Current mean: {int(statistics.mean(reading_list))}\n")

                i += 1
                time.sleep(1)

        else:
            raise ValueError(f'Using default values of {default_min}, {default_max}')
            return ((default_min, default_max))

        measured_min = int(statistics.mean(reading_list))

        print(f"Final Dry Mean: {int(measured_min)}")

        userinput = input("Please wet down the soil and press ENTER.")

        if userinput is not None:
            i = 0

            reading_list = []

            while i < 20:
                print(soil_sensor.moisture_read())
                reading_list.append(soil_sensor.moisture_read())


                print(f"Current mean: {int(statistics.mean(reading_list))}\n")

                i += 1
                time.sleep(1)

        else:
            raise ValueError(f'Using default values of {default_min}, {default_max}')
            return ((default_min, default_max))

        measured_max = int(statistics.mean(reading_list))


        print(f"Final Wet Mean: {measured_max}")

        return ((measured_min, measured_max))
    else:
        return (default_min, default_max)


def compute_soil_moisture_percentage(MIN, MAX, average_reading):
    """
    Use min and max soil readings to create percentage.
    currently based on static values.
    :param MIN: MIN_SOIL_MOISTURE
    :param MAX: MAX_SOIL_MOISTURE
    :param reading: reading from the probe
    """

    numerator = average_reading - MIN
    denomerator = MAX - MIN

    return (float(numerator/denomerator)*100)

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
SOIL_SENSOR_1_ADDRESS = 0x36
SOIL_SENSOR_2_ADDRESS = 0x37

DATA_FILE_ROOT = f"/home/david/pi_planter"

### Load data object ###
try:
    with open(f'{DATA_FILE_ROOT}/data_dict.json') as f:
        data_dict = json.load(f)
        logging.info('data_dict loaded from file.')
except FileNotFoundError:
    logging.info('Creating data_dict')
    data_dict = {}

try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=DISPLAY_ADDRESS, reset=oled_reset)
except Exception as e:
    logging.info(e)
### Configure soil sensor ###
try:
    soil_sensor_1 = Seesaw(i2c, addr=SOIL_SENSOR_1_ADDRESS)
except ValueError:
    print(f"No device at {hex(SOIL_SENSOR_1_ADDRESS)}. Make sure I2C is turned on in raspi-config.")
    logging.error(f"No device found at {hex(SOIL_SENSOR_1_ADDRESS)}. Exiting.")
    sys.exit()

try:
    soil_sensor_2 = Seesaw(i2c, addr=SOIL_SENSOR_2_ADDRESS)
except ValueError:
    print(f"No device at {hex(SOIL_SENSOR_2_ADDRESS)}. Make sure the AD0 jumper is soldered and try again.")
    logging.error(f"No device found at {hex(SOIL_SENSOR_2_ADDRESS)}. Exiting.")
    sys.exit()


### Calibrate sensor readings ###
MIN_SOIL_MOISTURE, MAX_SOIL_MOISTURE = calibrate_soil_sensor(calibrate=False, sensor_object=soil_sensor_1)

logging.info(f"MIN_SOIL_MOISTURE: {MIN_SOIL_MOISTURE}")
logging.info(f"MAX_SOIL_MOISTURE: {MAX_SOIL_MOISTURE}")

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

    ## Get and log data
    date_string = datetime.datetime.now().isoformat()
    logging.info(f"date_string: {date_string}")

    data_dict[date_string] = {}
    data_dict[date_string]['sensor1'] = {}
    data_dict[date_string]['sensor2'] = {}
    data_dict[date_string]['average'] = {}


    soil_sensor_1_moisture = soil_sensor_1.moisture_read()
    soil_sensor_2_moisture = soil_sensor_2.moisture_read()

    data_dict[date_string]['sensor1']['moisture'] = soil_sensor_1_moisture
    data_dict[date_string]['sensor2']['moisture'] = soil_sensor_2_moisture

    soil_moisture_average = (soil_sensor_1_moisture + soil_sensor_2_moisture) / 2

    data_dict[date_string]['average']['moisture'] = soil_moisture_average

    soil_sensor_1_temp = soil_sensor_1.get_temp()
    soil_sensor_2_temp = soil_sensor_2.get_temp()

    data_dict[date_string]['sensor1']['temp'] = soil_sensor_1_temp
    data_dict[date_string]['sensor2']['temp'] = soil_sensor_2_temp

    soil_temp_average = (soil_sensor_1_temp + soil_sensor_2_temp) / 2

    data_dict[date_string]['average']['temp'] = soil_temp_average

    logging.info(f"soil_sensor_1.moisture_read: {soil_sensor_1_moisture}")
    logging.info(f"soil_sensor_2.moisture_read: {soil_sensor_2_moisture}")
    logging.info(f"soil_moisture_average: {soil_moisture_average}")

    logging.info(f"soil_sensor_1.get_temp: {soil_sensor_1_temp:.1f}")
    logging.info(f"soil_sensor_2.get_temp: {soil_sensor_2_temp:.1f}")
    logging.info(f"soil_temp_average: {soil_temp_average}")


    logging.info(f"Moisture Calculated Percentage: {compute_soil_moisture_percentage(MIN_SOIL_MOISTURE, MAX_SOIL_MOISTURE, soil_moisture_average):.1f}")

    #text_string = f"Moisture%: {compute_soil_moisture_percentage(MIN_SOIL_MOISTURE, MAX_SOIL_MOISTURE, soil_moisture_average):.1f}\nTemp: {soil_temp_average:.1f}"
    text_string = f"moisture_avg: {soil_moisture_average}\nmoisture_%: {compute_soil_moisture_percentage(MIN_SOIL_MOISTURE, MAX_SOIL_MOISTURE, soil_moisture_average):.1f}\n{date_string}"

    logging.info(text_string)

    # Draw Some Text
    (font_width, font_height) = font.getbbox(text_string)[2:]

    draw.multiline_text((0,0), text_string, fill=255, align="left", font_size=10, spacing=6)

    # Display image
    oled.image(image)
    oled.show()

    with open('data_dict.json', 'w') as f:
        json.dump(data_dict, f)
    
    soil_sensor_1_moisture = None
    soil_sensor_2_moisture = None
    soil_moisture_average = None
    
    soil_sensor_1_temp = None
    soil_sensor_2_temp = None
    soil_temp_average = None

    time.sleep(10)
