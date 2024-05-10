"""
JSON Example written by AB
"""
import json

# JSON string:
# Multi-line string
dataString = """{
  "appliances": [
    {
      "name": "Living Room Light",
      "orientation": 0,
      "controls": [
        {
          "name": "Crimson Light",
          "ir_code": "#0000FF",
          "color": "0xFF0000"
        },
        {
          "name": "Magenta Light",
          "ir_code": "#0000FF",
          "color": "0xFF00FF"
        },
        {
          "name": "Sapphire Mode",
          "ir_code": "#0000FF",
          "color": "0x0000FF"
        },
        {
          "name": "Emerald Mode",
          "ir_code": "#0000FF",
          "color": "0x00FF00"
        },
        {
          "name": "Golden Up",
          "ir_code": "#0000FF",
          "color": "0xFFFF00"
        },
        {
          "name": "Azure Down",
          "ir_code": "#0000ff",
          "color": "0x00FFFF"
        }
      ]
    },
    {
      "name": "Kitchen Light",
      "orientation": 1,
      "controls": [
        {
          "name": "Coral Light",
          "ir_code": "#FF7F50",
          "color": "0xFF7F50"
        },
        {
          "name": "Lime Light",
          "ir_code": "#00FF00",
          "color": "0x00FF00"
        },
        {
          "name": "Ocean Mode",
          "ir_code": "#4169E1",
          "color": "0x4169E1"
        },
        {
          "name": "Ruby Mode",
          "ir_code": "#FF6347",
          "color": "0xFF6347"
        },
        {
          "name": "Topaz Up",
          "ir_code": "#00CED1",
          "color": "0x00CED1"
        },
        {
          "name": "Bronze Down",
          "ir_code": "#CD7F32",
          "color": "0xCD7F32"
        }
      ]
    },
    {
      "name": "Bedroom Light",
      "orientation": 2,
      "controls": [
        {
          "name": "Scarlet Light",
          "ir_code": "#FF2400",
          "color": "0xFF2400"
        },
        {
          "name": "Teal Light",
          "ir_code": "#008080",
          "color": "0x008080"
        },
        {
          "name": "Indigo Mode",
          "ir_code": "#4B0082",
          "color": "0x4B0082"
        },
        {
          "name": "Amber Mode",
          "ir_code": "#FFBF00",
          "color": "0xFFBF00"
        },
        {
          "name": "Platinum Up",
          "ir_code": "#E5E4E2",
          "color": "0xE5E4E2"
        },
        {
          "name": "Copper Down",
          "ir_code": "#B87333",
          "color": "0xB87333"
        }
      ]
    },
    {
      "name": "Office Light",
      "orientation": 3,
      "controls": [
        {
          "name": "Vermilion Light",
          "ir_code": "#E34234",
          "color": "0xE34234"
        },
        {
          "name": "Olive Light",
          "ir_code": "#808000",
          "color": "0x808000"
        },
        {
          "name": "Cobalt Mode",
          "ir_code": "#0047AB",
          "color": "0x0047AB"
        },
        {
          "name": "Pearl Mode",
          "ir_code": "#EAE0C8",
          "color": "0xEAE0C8"
        },
        {
          "name": "Silver Up",
          "ir_code": "#C0C0C0",
          "color": "0xC0C0C0"
        },
        {
          "name": "Brass Down",
          "ir_code": "#B5A642",
          "color": "0xB5A642"
        }
      ]
    }
  ]
}"""

# parse x:
data = json.loads(dataString)

# # Print the data stored
# print("PRINT ALL DATA IN DICT")
# print(data)
# 
# # Iterate over appliances
# print("Print All Appliances 1 by 1")
# for appliance in data["appliances"]:
#     print(appliance)
# 
#     # Print the Control 1 by 1
#     for control in appliance["controls"]:
#         print(control)
# 
# # Get me the colour for the 3rd control in the second appliance
# # You would have the current appliance based on the device rotation
# currentAppliance = 1 # indicates the second appliance in the list
# thirdControl = 2 # remember 0-based indexing
# colour = data["appliances"][currentAppliance]["controls"][thirdControl]["color"]
# print(f"The colour of the 3rd control in the second appliance is {colour}")



# # List to store control names for orientation = 0
# control_names_orientation_0 = []
# 
# # Iterate through appliances and their controls
# for appliance in data["appliances"]:
#     if appliance["orientation"] == 0:
#         for control in appliance["controls"]:
#             control_names_orientation_0.append(control["name"])
# 
# # Print the list of control names for orientation = 0
# print(control_names_orientation_0)


# # List to store color hex values for orientation = 0
# colors_hex = []
# 
# # Find the appliance with orientation = 0
# for appliance in data["appliances"]:
#     if appliance["orientation"] == 0:
#         # Extract controls for this appliance
#         controls = appliance["controls"]
#         # Extract color values (hex strings) for each control
#         for control in controls:
#             # Get the color string and convert to integer hex value
#             color_hex_str = control["color"]
#             # Convert hex string to integer hex value (without "0x" prefix)
#             color_hex_value = int(color_hex_str, 16)
#             # Append the integer hex value to the list of hex values
#             colors_hex.append(color_hex_value)
# 
# # Print the extracted color hex values for orientation = 0
# print("Hex Values of Colors (Orientation = 0):")
# print(colors_hex)

# List to store IR code hex values for orientation = 0
ir_codes_hex = []

# Find the appliance with orientation = 0
for appliance in data["appliances"]:
    if appliance["orientation"] == 0:
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

# Print the extracted IR code hex values for orientation = 0
print("Hex Values of IR Codes (Orientation = 0):")
print(ir_codes_hex)