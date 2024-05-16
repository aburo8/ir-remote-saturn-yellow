import os, sys, io
import M5
from M5 import *
import time
import json
from umqtt.simple import MQTTClient

# shapes used on screen
rect0 = None
rect4 = None
rect1 = None
rect5 = None
Title = None
rect2 = None
label_one = None
rect3 = None
label_two = None
label_three = None
label_four = None
label_five = None
label_six = None

# global variables 
configuration = 0
press = None
debounce = None
x = None
y = None
z = None
button = None
rotation = None
current_color = None
last_color = None
data = ""

#default configuration of remote
string = """{
  "appliances": [
    {
      "name": "Living Room Light",
      "orientation": 0,
      "controls": [
        {
          "name": "Crimson Light",
          "ir_code": "#000000",
          "color": [255, 255, 0]
        },
        {
          "name": "Magenta Light",
          "ir_code": "#000001",
          "color": [255, 255, 0]
        },
        {
          "name": "Sapphire Mode",
          "ir_code": "#000002",
          "color": [255, 255, 0]
        },
        {
          "name": "Emerald Mode",
          "ir_code": "#000003",
          "color": [255, 255, 0]
        },
        {
          "name": "Golden Up",
          "ir_code": "#000004",
          "color": [255, 255, 0]
        },
        {
          "name": "Azure Down",
          "ir_code": "#000005",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Kitchen Light",
      "orientation": 1,
      "controls": [
        {
          "name": "Coral Light",
          "ir_code": "#000006",
          "color": [255, 127, 80]
        },
        {
          "name": "Lime Light",
          "ir_code": "#000007",
          "color": [0, 255, 0]
        },
        {
          "name": "Ocean Mode",
          "ir_code": "#000008",
          "color": [65, 105, 225]
        },
        {
          "name": "Ruby Mode",
          "ir_code": "#000009",
          "color": [255, 99, 71]
        },
        {
          "name": "Topaz Up",
          "ir_code": "#00000A",
          "color": [0, 206, 209]
        },
        {
          "name": "Bronze Down",
          "ir_code": "#00000B",
          "color": [205, 127, 50]
        }
      ]
    },
    {
      "name": "Bedroom Light",
      "orientation": 2,
      "controls": [
        {
          "name": "Scarlet Light",
          "ir_code": "#00000C",
          "color": [255, 36, 0]
        },
        {
          "name": "Teal Light",
          "ir_code": "#00000D",
          "color": [0, 128, 128]
        },
        {
          "name": "Indigo Mode",
          "ir_code": "#00000E",
          "color": [75, 0, 130]
        },
        {
          "name": "Amber Mode",
          "ir_code": "#00000F",
          "color": [255, 191, 0]
        },
        {
          "name": "Platinum Up",
          "ir_code": "#000010",
          "color": [229, 228, 226]
        },
        {
          "name": "Copper Down",
          "ir_code": "#000011",
          "color": [181, 115, 50]
        }
      ]
    },
    {
      "name": "Office Light",
      "orientation": 3,
      "controls": [
        {
          "name": "Vermilion Light",
          "ir_code": "#000012",
          "color": [227, 66, 52]
        },
        {
          "name": "Olive Light",
          "ir_code": "#000013",
          "color": [128, 128, 0]
        },
        {
          "name": "Cobalt Mode",
          "ir_code": "#000014",
          "color": [0, 71, 171]
        },
        {
          "name": "Pearl Mode",
          "ir_code": "#000015",
          "color": [234, 224, 200]
        },
        {
          "name": "Silver Up",
          "ir_code": "#000016",
          "color": [192, 192, 192]
        },
        {
          "name": "Brass Down",
          "ir_code": "#000017",
          "color": [181, 166, 66]
        }
      ]
    }
  ]
}"""

# MQTT connection settings
server="broker.emqx.io"
ClientID = f'esp32-sub-{time.time_ns()}'
user = "emqx"
password = "public"
topic = "u47041165"
msg = b'{"msg":"hello"}'
client = MQTTClient(ClientID, server, 1883, user, password)

def sub(topic, msg):
    print("Updated configuration")
    global data, configuration
    data = json.loads(msg)
    configuration = 1
    
def connect():
    global topic
    client = MQTTClient(ClientID, server, 1883, user, password)
    client.set_callback(sub)
    client.connect()
    client.subscribe(topic)
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...' % (server))
    time.sleep(5)
    client.reconnect()

# screen configuration functions
def rgb_to_hex(rgb):
    """Convert RGB values to a hexadecimal color string."""
    r = max(0, min(255, rgb[0]))
    g = max(0, min(255, rgb[1]))
    b = max(0, min(255, rgb[2]))
    hex_color = "0x{:02X}{:02X}{:02X}".format(r, g, b)
    return hex_color
  
  
def zero_degree_screen():

    global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, data
    # set rotation
    Widgets.setRotation(1)
    Widgets.fillScreen(0x222222)
    
    # List to store appliance names
    appliance_names = []
    # Iterate over each appliance in the "appliances" list
    for appliance in data["appliances"]:
        # Extract the "name" of the appliance and append to the list
        appliance_names.append(appliance["name"])
    Title = Widgets.Title(appliance_names[0], 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)

    rect0 = Widgets.Rectangle(40, 40, 50, 50, 0xffffff, 0xffffff)
    rect1 = Widgets.Rectangle(140, 40, 50, 50, 0xffffff, 0xffffff)
    rect2 = Widgets.Rectangle(240, 40, 50, 50, 0xffffff, 0xffffff)
    rect3 = Widgets.Rectangle(40, 140, 50, 50, 0xffffff, 0xffffff)
    rect4 = Widgets.Rectangle(140, 140, 50, 50, 0xffffff, 0xffffff)
    rect5 = Widgets.Rectangle(240, 140, 50, 50, 0xffffff, 0xffffff)
    # List to store color hex values for orientation = 0
    colors_hex = []
    # Find the appliance with orientation = 0
    for appliance in data["appliances"]:
        if appliance["orientation"] == 0:
            # Extract controls for this appliance
            controls = appliance["controls"]
            # Extract color values (hex strings) for each control
            for control in controls:
                # Extract rgb format
                rgb_color = control["color"]
                # Convert rgb format to hex
                color_hex_str = rgb_to_hex(rgb_color)
                # Convert hex string to integer hex value (without "0x" prefix)
                color_hex_value = int(color_hex_str, 16)
                # Append the integer hex value to the list of hex values
                colors_hex.append(color_hex_value)
    rect0.setColor(color=colors_hex[0], fill_c=colors_hex[0])
    rect1.setColor(color=colors_hex[1], fill_c=colors_hex[1])
    rect2.setColor(color=colors_hex[2], fill_c=colors_hex[2])
    rect3.setColor(color=colors_hex[3], fill_c=colors_hex[3])
    rect4.setColor(color=colors_hex[4], fill_c=colors_hex[4])
    rect5.setColor(color=colors_hex[5], fill_c=colors_hex[5])
    
    # List to store control names for orientation = 0
    control_names_orientation_0 = []
    # Iterate through appliances and their controls
    for appliance in data["appliances"]:
        if appliance["orientation"] == 0:
            for control in appliance["controls"]:
                control_names_orientation_0.append(control["name"])
      
    label_one = Widgets.Label(control_names_orientation_0[0], 25, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_two = Widgets.Label(control_names_orientation_0[1], 125, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_three = Widgets.Label(control_names_orientation_0[2], 225, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_four = Widgets.Label(control_names_orientation_0[3], 25, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_five = Widgets.Label(control_names_orientation_0[4], 125, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_six = Widgets.Label(control_names_orientation_0[5], 225, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def ninety_degree_screen():

    global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, data
    # set rotation
    Widgets.setRotation(0)
    Widgets.fillScreen(0x222222)
    
    # List to store appliance names
    appliance_names = []

    # Iterate over each appliance in the "appliances" list
    for appliance in data["appliances"]:
        # Extract the "name" of the appliance and append to the list
        appliance_names.append(appliance["name"])
        
    Title = Widgets.Title(appliance_names[1], 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
    
    # color in rectangles
    rect0 = Widgets.Rectangle(30, 40, 50, 50, 0xffffff, 0xffffff)
    rect1 = Widgets.Rectangle(130, 40, 50, 50, 0xffffff, 0xffffff)
    rect2 = Widgets.Rectangle(30, 140, 50, 50, 0xffffff, 0xffffff)
    rect3 = Widgets.Rectangle(130, 140, 50, 50, 0xffffff, 0xffffff)
    rect4 = Widgets.Rectangle(30, 240, 50, 50, 0xffffff, 0xffffff)
    rect5 = Widgets.Rectangle(130, 240, 50, 50, 0xffffff, 0xffffff)
    # List to store color hex values for orientation = 0
    colors_hex = []
    # Find the appliance with orientation = 0
    for appliance in data["appliances"]:
        if appliance["orientation"] == 1:
            # Extract controls for this appliance
            controls = appliance["controls"]
            # Extract color values (hex strings) for each control
            for control in controls:
                # Extract rgb format
                rgb_color = control["color"]
                # Convert rgb format to hex
                color_hex_str = rgb_to_hex(rgb_color)
                # Convert hex string to integer hex value (without "0x" prefix)
                color_hex_value = int(color_hex_str, 16)
                # Append the integer hex value to the list of hex values
                colors_hex.append(color_hex_value)
    rect0.setColor(color=colors_hex[0], fill_c=colors_hex[0])
    rect1.setColor(color=colors_hex[1], fill_c=colors_hex[1])
    rect2.setColor(color=colors_hex[2], fill_c=colors_hex[2])
    rect3.setColor(color=colors_hex[3], fill_c=colors_hex[3])
    rect4.setColor(color=colors_hex[4], fill_c=colors_hex[4])
    rect5.setColor(color=colors_hex[5], fill_c=colors_hex[5])
  
    # List to store control names for orientation = 1
    control_names_orientation_1 = []
    # Iterate through appliances and their controls
    for appliance in data["appliances"]:
        if appliance["orientation"] == 1:
            for control in appliance["controls"]:
                control_names_orientation_1.append(control["name"])
    label_one = Widgets.Label(control_names_orientation_1[0], 30, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_two = Widgets.Label(control_names_orientation_1[1], 130, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_three = Widgets.Label(control_names_orientation_1[2], 30, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_four = Widgets.Label(control_names_orientation_1[3], 130, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_five = Widgets.Label(control_names_orientation_1[4], 30, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_six = Widgets.Label(control_names_orientation_1[5], 130, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def one_eighty_degree_screen():

    global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, data
    # set rotation
    Widgets.setRotation(3)
    Widgets.fillScreen(0x222222)
    
    # List to store appliance names
    appliance_names = []

    # Iterate over each appliance in the "appliances" list
    for appliance in data["appliances"]:
        # Extract the "name" of the appliance and append to the list
        appliance_names.append(appliance["name"])
        
    Title = Widgets.Title(appliance_names[2], 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)

    rect0 = Widgets.Rectangle(40, 40, 50, 50, 0xffffff, 0xffffff)
    rect1 = Widgets.Rectangle(140, 40, 50, 50, 0xffffff, 0xffffff)
    rect2 = Widgets.Rectangle(240, 40, 50, 50, 0xffffff, 0xffffff)
    rect3 = Widgets.Rectangle(40, 140, 50, 50, 0xffffff, 0xffffff)
    rect4 = Widgets.Rectangle(140, 140, 50, 50, 0xffffff, 0xffffff)
    rect5 = Widgets.Rectangle(240, 140, 50, 50, 0xffffff, 0xffffff)
    # List to store color hex values for orientation = 2
    colors_hex = []
    # Find the appliance with orientation = 2
    for appliance in data["appliances"]:
        if appliance["orientation"] == 2:
            # Extract controls for this appliance
            controls = appliance["controls"]
            # Extract color values (hex strings) for each control
            for control in controls:
                # Extract rgb format
                rgb_color = control["color"]
                # Convert rgb format to hex
                color_hex_str = rgb_to_hex(rgb_color)
                # Convert hex string to integer hex value (without "0x" prefix)
                color_hex_value = int(color_hex_str, 16)
                # Append the integer hex value to the list of hex values
                colors_hex.append(color_hex_value)
    rect0.setColor(color=colors_hex[0], fill_c=colors_hex[0])
    rect1.setColor(color=colors_hex[1], fill_c=colors_hex[1])
    rect2.setColor(color=colors_hex[2], fill_c=colors_hex[2])
    rect3.setColor(color=colors_hex[3], fill_c=colors_hex[3])
    rect4.setColor(color=colors_hex[4], fill_c=colors_hex[4])
    rect5.setColor(color=colors_hex[5], fill_c=colors_hex[5])

    # List to store control names for orientation = 2
    control_names_orientation_2 = []

    # Iterate through appliances and their controls
    for appliance in data["appliances"]:
        if appliance["orientation"] == 2:
            for control in appliance["controls"]:
                control_names_orientation_2.append(control["name"])
      
    label_one = Widgets.Label(control_names_orientation_2[0], 25, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_two = Widgets.Label(control_names_orientation_2[1], 125, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_three = Widgets.Label(control_names_orientation_2[2], 225, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_four = Widgets.Label(control_names_orientation_2[3], 25, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_five = Widgets.Label(control_names_orientation_2[4], 125, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_six = Widgets.Label(control_names_orientation_2[5], 225, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def two_seventy_degree_screen():

    global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
    # set rotation
    Widgets.setRotation(2)
    Widgets.fillScreen(0x222222)
    
    # List to store appliance names
    appliance_names = []

    # Iterate over each appliance in the "appliances" list
    for appliance in data["appliances"]:
        # Extract the "name" of the appliance and append to the list
        appliance_names.append(appliance["name"])
        
    Title = Widgets.Title(appliance_names[3], 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
    
    #re-shuffle rectangles
    rect0 = Widgets.Rectangle(30, 40, 50, 50, 0xffffff, 0xffffff)
    rect1 = Widgets.Rectangle(130, 40, 50, 50, 0xffffff, 0xffffff)
    rect2 = Widgets.Rectangle(30, 140, 50, 50, 0xffffff, 0xffffff)
    rect3 = Widgets.Rectangle(130, 140, 50, 50, 0xffffff, 0xffffff)
    rect4 = Widgets.Rectangle(30, 240, 50, 50, 0xffffff, 0xffffff)
    rect5 = Widgets.Rectangle(130, 240, 50, 50, 0xffffff, 0xffffff)
    # List to store color hex values for orientation = 3
    colors_hex = []
    # Find the appliance with orientation = 3
    for appliance in data["appliances"]:
        if appliance["orientation"] == 3:
            # Extract controls for this appliance
            controls = appliance["controls"]
            # Extract color values (hex strings) for each control
            for control in controls:
                # Extract rgb format
                rgb_color = control["color"]
                # Convert rgb format to hex
                color_hex_str = rgb_to_hex(rgb_color)
                # Convert hex string to integer hex value (without "0x" prefix)
                color_hex_value = int(color_hex_str, 16)
                # Append the integer hex value to the list of hex values
                colors_hex.append(color_hex_value)
    rect0.setColor(color=colors_hex[0], fill_c=colors_hex[0])
    rect1.setColor(color=colors_hex[1], fill_c=colors_hex[1])
    rect2.setColor(color=colors_hex[2], fill_c=colors_hex[2])
    rect3.setColor(color=colors_hex[3], fill_c=colors_hex[3])
    rect4.setColor(color=colors_hex[4], fill_c=colors_hex[4])
    rect5.setColor(color=colors_hex[5], fill_c=colors_hex[5])
    
    # List to store control names for orientation = 3
    control_names_orientation_3 = []

    # Iterate through appliances and their controls
    for appliance in data["appliances"]:
        if appliance["orientation"] == 3:
            for control in appliance["controls"]:
                control_names_orientation_3.append(control["name"])

    label_one = Widgets.Label(control_names_orientation_3[0], 30, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_two = Widgets.Label(control_names_orientation_3[1], 130, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_three = Widgets.Label(control_names_orientation_3[2], 30, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_four = Widgets.Label(control_names_orientation_3[3], 130, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_five = Widgets.Label(control_names_orientation_3[4], 30, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_six = Widgets.Label(control_names_orientation_3[5], 130, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)

# set up functions
def setup():
  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, data, string, client

  M5.begin()
  
  # initialize mqtt
  try:
    client = connect()
  except OSError as e:
    reconnect()
    
  print('Connected to MQTT Broker "%s"' % (server))  
  
  # if code reaches here, mqtt has succesfully been setup
  data = json.loads(string)
  zero_degree_screen()

  press = 0
  debounce = 0
  button = 0
  x = 0
  y = 0
  z = 0
  last_color = 0
  current_color = 0


def loop():
  
  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, client
  M5.update()
  
  # non-blocking check mqtt message function
  client.check_msg()
  
  # determine rotation of device 
  (x, y, z) = Imu.getAccel()
  if x < 0.1 and x > -0.1 and y > 0.9 and y < 1.1:
    rotation = 0
    current_color = rotation
  elif x > -1.1 and x < -0.9 and y < 0.1 and y > -0.1:
    rotation = 1
    current_color = rotation
  elif x > -0.1 and x < 0.1 and y > -1.1 and y < -0.9:
    rotation = 2
    current_color = rotation
  elif x < 1.1 and x > 0.9 and y > -0.1 and y < 0.1:
    rotation = 3
    current_color = rotation

  # update color of buttons from rotation (if rotation has changed)
  if last_color != current_color:
    if rotation==0:
      zero_degree_screen()
    elif rotation==1:
      ninety_degree_screen()
    elif rotation==2:
      one_eighty_degree_screen()
    elif rotation==3:
      two_seventy_degree_screen()
      
    last_color = current_color
    
  # update screen if mqtt message has been recieved
  if configuration == 1:
    if rotation==0:
      zero_degree_screen()
    elif rotation==1:
      ninety_degree_screen()
    elif rotation==2:
      one_eighty_degree_screen()
    elif rotation==3:
      two_seventy_degree_screen()
      
    configuration = 0
    
  # process any button presses from device
  if (M5.Touch.getX()) < 110 and (M5.Touch.getY()) < 120 and (M5.Touch.getCount()) > 0:
      
    if rotation == 0:
      button = 1
    elif rotation == 1:
        button = 2
    elif rotation == 2:
        button = 6
    elif rotation == 3:
        button = 5
    press = 1
    debounce = time.time()
    
  elif (M5.Touch.getX()) < 110 and (M5.Touch.getY()) > 120 and (M5.Touch.getCount()) > 0:
      
    if rotation == 0:
        button = 4
    elif rotation == 1:
        button = 1
    elif rotation == 2:
        button = 3
    elif rotation == 3:
        button = 6
    press = 1
    debounce = time.time()
    
  elif (M5.Touch.getX()) > 200 and (M5.Touch.getY()) < 120 and (M5.Touch.getCount()) > 0:
    
    if rotation == 0:
        button = 3
    elif rotation == 1:
        button = 6
    elif rotation == 2:
        button = 4
    elif rotation == 3:
        button = 1
    press = 1
    debounce = time.time()
    
  elif (M5.Touch.getX()) > 200 and (M5.Touch.getY()) > 120 and (M5.Touch.getCount()) > 0:
    
    if rotation == 0:
        button = 6
    elif rotation == 1:
        button = 5
    elif rotation == 2:
        button = 1
    elif rotation == 3:
        button = 2
    press = 1
    debounce = time.time()
    
  elif (M5.Touch.getY()) < 120 and (M5.Touch.getX()) > 110 and (M5.Touch.getX()) < 200 and (M5.Touch.getCount()) > 0:

    if rotation == 0:
        button = 2
    elif rotation == 1:
        button = 4
    elif rotation == 2:
        button = 5
    elif rotation == 3:
        button = 3
    press = 1
    debounce = time.time()
    
  elif (M5.Touch.getY()) > 120 and (M5.Touch.getX()) > 110 and (M5.Touch.getX()) < 200 and (M5.Touch.getCount()) > 0:
    button = 5
    
    if rotation == 0:
        button = 5
    elif rotation == 1:
        button = 3
    elif rotation == 2:
        button = 2
    elif rotation == 3:
        button = 4
    press = 1
    debounce = time.time()
  
  # execute button presses
  if press == 1 and (time.time()) - debounce >= 1:
    press = 0
    ir_codes_hex = []
    for appliance in data["appliances"]:
        if appliance["orientation"] == rotation:
            # Extract controls for this appliance
            controls = appliance["controls"]
            # Extract IR codes (hex strings) for each control
            for control in controls:
                # Get the IR code string and convert to integer hex value
                ir_code_hex_str = control["ir_code"]
                # Remove "#" prefix and convert hex string to integer hex value
                ir_code_hex_value = int(ir_code_hex_str[1:], 16)
                # Append the integer hex value to the list of IR code hex values
                ir_codes_hex.append(ir_code_hex_value)
                
    print((str('IR code sent: ') + str(ir_codes_hex[button - 1])))
    message = (str("{\"IR\": ") + str(ir_codes_hex[button - 1])) + str('}')
    IR_topic = "IR_topic"
    
    # if message send fails, reconnect
    try:
        print('Sending message %s on topic %s' % (message, IR_topic))
        client.publish(IR_topic, message, qos=0)
    except Exception as e:
        print('Failed to publish message:', e)
        client = reconnect()


# Main function
if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")