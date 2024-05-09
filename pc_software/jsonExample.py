"""
JSON Example written by AB
"""
import json

# JSON string:
# Multi-line string
dataString = """{
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
    }
  ]
}"""

# parse x:
data = json.loads(dataString)

# Print the data stored
print("PRINT ALL DATA IN DICT")
print(data)

# Iterate over appliances
print("Print All Appliances 1 by 1")
for appliance in data["appliances"]:
    print(appliance)

    # Print the Control 1 by 1
    for control in appliance["controls"]:
        print(control)

# Get me the colour for the 3rd control in the second appliance
# You would have the current appliance based on the device rotation
currentAppliance = 1 # indicates the second appliance in the list
thirdControl = 2 # remember 0-based indexing
colour = data["appliances"][currentAppliance]["controls"][thirdControl]["color"]
print(f"The colour of the 3rd control in the second appliance is {colour}")