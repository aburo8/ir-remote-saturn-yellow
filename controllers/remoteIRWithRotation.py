import os, sys, io
import M5
from M5 import *
import time


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

# Describe this function...
def set_rectangles_blue():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect1.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect2.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect3.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect4.setColor(color=0x3333ff, fill_c=0x3333ff)
  rect5.setColor(color=0x3333ff, fill_c=0x3333ff)

# Describe this function...
def set_rectangles_yellow():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0xffff33, fill_c=0xffff33)
  rect1.setColor(color=0xffff00, fill_c=0xffff00)
  rect2.setColor(color=0xffff00, fill_c=0xffff00)
  rect3.setColor(color=0xffff00, fill_c=0xffff00)
  rect4.setColor(color=0xffff00, fill_c=0xffff33)
  rect5.setColor(color=0xffff00, fill_c=0xffff00)

# Describe this function...
def set_rectangles_red():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0xff0000, fill_c=0xff0000)
  rect1.setColor(color=0xff0000, fill_c=0xff0000)
  rect2.setColor(color=0xff0000, fill_c=0xff0000)
  rect3.setColor(color=0xff0000, fill_c=0xff0000)
  rect4.setColor(color=0xff0000, fill_c=0xff0000)
  rect5.setColor(color=0xff0000, fill_c=0xff0000)

# Describe this function...
def set_rectangles_green():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color, rect0, rect4, rect1, rect5, Title, rect2, label_one, rect3, label_two, label_three, label_four, label_five, label_six
  rect0.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect1.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect2.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect3.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect4.setColor(color=0x33ff33, fill_c=0x33ff33)
  rect5.setColor(color=0x33ff33, fill_c=0x33ff33)


def updateScreenRotation(rotation): # rotation here is 0-3
  global rect0, rect1, rect2, rect3, rect4, rect5, Title, label_one, label_two, label_three, label_four, label_five, label_six
  # update your global state variables
  # these should store the current appliance index
  if rotation == 0:
    # write code to rebuild 0 here.
    # Set colour based on the JSON File orientation & colour properties
    pass
  elif rotation == 1:
    pass
    
  Widgets.setRotation(rotation)
  Widgets.fillScreen(0x222222)
  rect0 = Widgets.Rectangle(35, 40, 30, 30, 0xffffff, 0xffffff)
  rect4 = Widgets.Rectangle(243, 40, 30, 30, 0xffffff, 0xffffff)
  rect1 = Widgets.Rectangle(139, 40, 30, 31, 0xffffff, 0xffffff)
  rect5 = Widgets.Rectangle(242, 158, 30, 30, 0xffffff, 0xffffff)
  Title = Widgets.Title("IR Remote", 3, 0xffffff, 0x0000FF, Widgets.FONTS.DejaVu18)
  rect2 = Widgets.Rectangle(37, 161, 30, 30, 0xffffff, 0xffffff)
  label_one = Widgets.Label("1", 46, 76, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  rect3 = Widgets.Rectangle(140, 159, 30, 30, 0xffffff, 0xffffff)
  label_two = Widgets.Label("2", 148, 78, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_three = Widgets.Label("3", 254, 83, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_four = Widgets.Label("4", 47, 198, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_five = Widgets.Label("5", 149, 195, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_six = Widgets.Label("6", 254, 195, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

def setup():
  global configuration, press, debounce, x, y, z, button, rotation, current_color, last_color

  M5.begin()
  
  updateScreenRotation(1)

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
  (x, y, z) = Imu.getAccel()
  if x < 0.1 and x > -0.1 and y > 0.9 and y < 1.1:
    rotation = 0
    updateScreenRotation(0)
    current_color = rotation
  elif x > -1.1 and x < -0.9 and y < 0.1 and y > -0.1:
    rotation = 90
    current_color = rotation
    updateScreenRotation(1)
  elif x > -0.1 and x < 0.1 and y > -1.1 and y < -0.9:
    rotation = 180
    current_color = rotation
  elif x < 1.1 and x > 0.9 and y > -0.1 and y < 0.1:
    rotation = 270
    current_color = rotation
    updateScreenRotation(2)
  if (M5.Touch.getX()) < 110 and (M5.Touch.getY()) < 120 and (M5.Touch.getCount()) > 0:
    button = 1
    press = 1
    debounce = time.time()
    rect0.setColor(color=0x6600cc, fill_c=0x6600cc)
  elif (M5.Touch.getX()) < 110 and (M5.Touch.getY()) > 120 and (M5.Touch.getCount()) > 0:
    button = 4
    press = 1
    debounce = time.time()
  elif (M5.Touch.getX()) > 200 and (M5.Touch.getY()) < 120 and (M5.Touch.getCount()) > 0:
    button = 3
    press = 1
    debounce = time.time()
  elif (M5.Touch.getX()) > 200 and (M5.Touch.getY()) > 120 and (M5.Touch.getCount()) > 0:
    button = 6
    press = 1
    debounce = time.time()
  elif (M5.Touch.getY()) < 120 and (M5.Touch.getX()) > 110 and (M5.Touch.getX()) < 200 and (M5.Touch.getCount()) > 0:
    button = 2
    press = 1
    debounce = time.time()
  elif (M5.Touch.getY()) > 120 and (M5.Touch.getX()) > 110 and (M5.Touch.getX()) < 200 and (M5.Touch.getCount()) > 0:
    button = 5
    press = 1
    debounce = time.time()
  if last_color != current_color:
    if rotation==0:
      set_rectangles_blue()
    elif rotation==90:
      set_rectangles_green()
    elif rotation==180:
      set_rectangles_red()
    elif rotation==270:
      set_rectangles_yellow()
    else:
      set_rectangles_blue()
    last_color = current_color
  if press == 1 and (time.time()) - debounce >= 1:
    press = 0
    print((str('Button number: ') + str(button)))


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
