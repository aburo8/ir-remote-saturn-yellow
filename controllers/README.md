# M5Core2 Controller Docs
- Flashing the controllers
1. Follow the instructions on the M5Burner app to download the Micropython firmware UIFlow2.0 onto the M5Core2 device. 
2. Flash the remoteIR.py file to an M5Core2 device using the Thonny IDE. This is detailed well in the official Thonny Wiki for Micropython:
   https://github.com/thonny/thonny/wiki/MicroPython

- Flashing the transmitter
1. Flash the ir_transmitter_arduino.ino file onto a M5Core2 device using the arduino IDE. This process is documented in the official M5 docs website:
   https://docs.m5stack.com/en/arduino/arduino_ide.
2. Connect the pinout in the following configuration shown in the schematic below. 
