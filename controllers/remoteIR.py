import os, sys, io
import M5
from M5 import *
import time
import json

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
configuration = None
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

string = """{
  "appliances": [
    {
      "name": "Light Bar",
      "orientation": 0,
      "controls": [
        {
          "name": "Red Light",
          "ir_code": "#FFFFFF",
          "color": [255, 255, 255]
        },
        {
          "name": "Purple Light",
          "ir_code": "#000000",
          "color": [0, 0, 0]
        },
        {
          "name": "Fade Mode",
          "ir_code": "#FF0000",
          "color": [255, 0, 0]
        },
        {
          "name": "Stripe Mode",
          "ir_code": "#00FF00",
          "color": [0, 255, 0]
        },
        {
          "name": "Brightness Up",
          "ir_code": "#0000FF",
          "color": [0, 0, 255]
        },
        {
          "name": "Brightness Down",
          "ir_code": "#FFFF00",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Light Bar",
      "orientation": 1,
      "controls": [
        {
          "name": "Red Light",
          "ir_code": "#FFFFFF",
          "color": [255, 255, 255]
        },
        {
          "name": "Purple Light",
          "ir_code": "#000000",
          "color": [0, 0, 0]
        },
        {
          "name": "Fade Mode",
          "ir_code": "#FF0000",
          "color": [255, 0, 0]
        },
        {
          "name": "Stripe Mode",
          "ir_code": "#00FF00",
          "color": [0, 255, 0]
        },
        {
          "name": "Brightness Up",
          "ir_code": "#0000FF",
          "color": [0, 0, 255]
        },
        {
          "name": "Brightness Down",
          "ir_code": "#FFFF00",
          "color": [255, 255, 0]
        }
      ]
    }
  ]
}"""


def set_rectangles_blue():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect1.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect2.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect3.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect4.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect5.setColor(color=0x3333ff, fill_c=0x3333ff)

def set_rectangles_yellow():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0xffff00, fill_c=0xffff00)
  rect1.setColor(color=0xffff00, fill_c=0xffff00)
  rect2.setColor(color=0xffff00, fill_c=0xffff00)
  rect3.setColor(color=0xffff00, fill_c=0xffff00)
  rect4.setColor(color=0xffff00, fill_c=0xffff00)
  rect5.setColor(color=0xffff00, fill_c=0xffff00)

def set_rectangles_red():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0xff0000, fill_c=0xff0000)
  rect1.setColor(color=0xff0000, fill_c=0xff0000)
  rect2.setColor(color=0xff0000, fill_c=0xff0000)
  rect3.setColor(color=0xff0000, fill_c=0xff0000)
  rect4.setColor(color=0xff0000, fill_c=0xff0000)
  rect5.setColor(color=0xff0000, fill_c=0xff0000)

def set_rectangles_green():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect1.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect2.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect3.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect4.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect5.setColor(color=0x33ff33, fill_c=0x33ff33)
  
  
def zero_degree_screen():

    global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, data
    # set rotation
    Widgets.setRotation(1)
    Widgets.fillScreen(0x222222)
    Title = Widgets.Title("IR Remote", 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)

    rect0 = Widgets.Rectangle(40, 40, 50, 50, 0xffffff, 0xffffff)
    rect1 = Widgets.Rectangle(140, 40, 50, 50, 0xffffff, 0xffffff)
    rect2 = Widgets.Rectangle(240, 40, 50, 50, 0xffffff, 0xffffff)
    rect3 = Widgets.Rectangle(40, 140, 50, 50, 0xffffff, 0xffffff)
    rect4 = Widgets.Rectangle(140, 140, 50, 50, 0xffffff, 0xffffff)
    rect5 = Widgets.Rectangle(240, 140, 50, 50, 0xffffff, 0xffffff)
      
    # List to store control names for orientation = 0
    control_names_orientation_0 = []

    # Iterate through appliances and their controls
    for appliance in data["appliances"]:
        if appliance["orientation"] == 0:
            for control in appliance["controls"]:
                control_names_orientation_0.append(control["name"])
      
    label_one = Widgets.Label(control_names_orientation_0[0], 30, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_two = Widgets.Label(control_names_orientation_0[1], 130, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_three = Widgets.Label(control_names_orientation_0[2], 230, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_four = Widgets.Label(control_names_orientation_0[3], 30, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_five = Widgets.Label(control_names_orientation_0[4], 130, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
    label_six = Widgets.Label(control_names_orientation_0[5], 230, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def ninety_degree_screen():

  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  # set rotation
  Widgets.setRotation(0)
  Widgets.fillScreen(0x222222)
  Title = Widgets.Title("IR Remote", 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
  #re-shuffle rectangles
  rect0 = Widgets.Rectangle(30, 40, 50, 50, 0xffffff, 0xffffff)
  rect1 = Widgets.Rectangle(130, 40, 50, 50, 0xffffff, 0xffffff)
  rect2 = Widgets.Rectangle(30, 140, 50, 50, 0xffffff, 0xffffff)
  rect3 = Widgets.Rectangle(130, 140, 50, 50, 0xffffff, 0xffffff)
  rect4 = Widgets.Rectangle(30, 240, 50, 50, 0xffffff, 0xffffff)
  rect5 = Widgets.Rectangle(130, 240, 50, 50, 0xffffff, 0xffffff)
  #re-shuffle labels
  label_one = Widgets.Label("1", 50, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_two = Widgets.Label("2", 150, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_three = Widgets.Label("3", 50, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_four = Widgets.Label("4", 150, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_five = Widgets.Label("5", 50, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_six = Widgets.Label("6", 150, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def one_eighty_degree_screen():

  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  # set rotation
  Widgets.setRotation(3)
  Widgets.fillScreen(0x222222)
  Title = Widgets.Title("IR Remote", 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
  
  rect0 = Widgets.Rectangle(40, 40, 50, 50, 0xffffff, 0xffffff)
  rect1 = Widgets.Rectangle(140, 40, 50, 50, 0xffffff, 0xffffff)
  rect2 = Widgets.Rectangle(240, 40, 50, 50, 0xffffff, 0xffffff)
  rect3 = Widgets.Rectangle(40, 140, 50, 50, 0xffffff, 0xffffff)
  rect4 = Widgets.Rectangle(140, 140, 50, 50, 0xffffff, 0xffffff)
  rect5 = Widgets.Rectangle(240, 140, 50, 50, 0xffffff, 0xffffff)
  
  label_one = Widgets.Label("1", 50, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_two = Widgets.Label("2", 150, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_three = Widgets.Label("3", 250, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_four = Widgets.Label("4", 50, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_five = Widgets.Label("5", 150, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_six = Widgets.Label("6", 250, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  
def two_seventy_degree_screen():

  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  # set rotation
  Widgets.setRotation(2)
  Widgets.fillScreen(0x222222)
  Title = Widgets.Title("IR Remote", 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
  #re-shuffle rectangles
  rect0 = Widgets.Rectangle(30, 40, 50, 50, 0xffffff, 0xffffff)
  rect1 = Widgets.Rectangle(130, 40, 50, 50, 0xffffff, 0xffffff)
  rect2 = Widgets.Rectangle(30, 140, 50, 50, 0xffffff, 0xffffff)
  rect3 = Widgets.Rectangle(130, 140, 50, 50, 0xffffff, 0xffffff)
  rect4 = Widgets.Rectangle(30, 240, 50, 50, 0xffffff, 0xffffff)
  rect5 = Widgets.Rectangle(130, 240, 50, 50, 0xffffff, 0xffffff)
  #re-shuffle labels
  label_one = Widgets.Label("1", 50, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_two = Widgets.Label("2", 150, 100, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_three = Widgets.Label("3", 50, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_four = Widgets.Label("4", 150, 200, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_five = Widgets.Label("5", 50, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)
  label_six = Widgets.Label("6", 150, 300, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9)


def setup():
  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, data, string

  M5.begin()
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
  set_rectangles_blue()


def loop():
  
  global rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six, configuration, press, debounce, x, y, z, button, rotation, current_color, last_color
  M5.update()
  
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
      set_rectangles_blue()
    elif rotation==1:
      ninety_degree_screen()
      set_rectangles_green()
    elif rotation==2:
      one_eighty_degree_screen()
      set_rectangles_red()
    elif rotation==3:
      two_seventy_degree_screen()
      set_rectangles_yellow()
    else:
      set_rectangles_blue()
    last_color = current_color
    
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
    print((str('Button number: ') + str(button)))


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
