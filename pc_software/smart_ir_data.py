"""
Data structures for the Smart-Ir: Universal Remote Control System
Written by AB
"""
from dataclasses import dataclass
from typing import List

# Constants
VERSION = 1.0 # Version of the configuration data
ORIENTATION_UP = 0
ORIENTATION_RIGHT = 1
ORIENTATION_DOWN = 2
ORIENTATION_LEFT = 3

@dataclass
class Control:
    """
    IR Control to transmit
    """
    label: str # control label
    irCode: bytes # bytes to transmit
    irCodeLen: int # number of bytes to transmit
    colour: List[int] # control colour


@dataclass
class Appliance:
    """
    Appliance data within the configuration file
    """
    name: str # Appliance name
    orientation: int # Appliance orientation 0-3 (see constants section)
    controls: List[Control] # controls for the associated appliance

@dataclass
class ControllerConfig:
    """
    The Configuration data transmitted to the M5Core2 Universal Remote Controllers
    """
    version: float
    appliances: List[Appliance] # appliances within the configuration

def generate_base_appliance(name):
    """
    Generates a base appliance with default values
    """
    controls = []
    for i in range(6):
        # Add basic controls
        control = Control(f"Control {i+1}", bytes.fromhex("FFFFFF"), 3, [0, 0, 255])
        controls.append(control)

    appliance = Appliance(name, ORIENTATION_UP, controls)

    return appliance

def orientation_to_string(orientation):
    """
    Converts an orientation to it's string representation
    """
    if orientation == ORIENTATION_DOWN:
        return "Down (180 Degrees)"
    elif orientation == ORIENTATION_LEFT:
        return "Left (270 Degrees)"
    elif orientation == ORIENTATION_RIGHT:
        return "Right (90 Degrees)"
    elif orientation == ORIENTATION_UP:
        return "Up (0 Degrees)"
    else:
        return ""