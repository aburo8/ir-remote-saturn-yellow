"""
Data structures for the Smart-Ir: Universal Remote Control System
Written by AB
"""
from dataclasses import dataclass, asdict
from typing import List
import os
import json

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
    irCode: int # byte to transmit (uint32)
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

    def to_dict(self):
        return asdict(self)
    
    def save_to_disk(self, customPath = None):
        """
        Saves the controller configuration to disk
        """
        savePath = ("./user_data/controller_configuration.json" if customPath is None else customPath)

        try:          
            # save to disk
            if os.path.isdir(os.path.abspath("./user_data")) is False:
                os.makedirs(os.path.abspath("./user_data"))
                print("user_data directory created!")

            with open(os.path.abspath(savePath), "w") as f:
                data = json.dumps(self.to_dict(), indent=4)
                f.write(data)
                print("Controller Configuration File Saved")
        except FileExistsError:
            print("Unable to save Controller Configuration")
    
    def load_from_disk(self, customPath = None):
        """
        Loads the controller configuration to disk
        """
        loadPath = ("./user_data/controller_configuration.json" if customPath is None else customPath)

        # Try and make the user_data folder to avoid errors
        try:
            if os.path.isdir(os.path.abspath("./user_data")) is False:
                os.makedirs(os.path.abspath("./user_data"))
                print("user_data directory created!")
                raise FileNotFoundError()
            else:
                print("user_data directory already exists!")
                
            with open(os.path.abspath(loadPath), "r") as f:
                fileData = json.load(f)
                if self.version != fileData["version"]:
                    print("Controller configuration outdated! Creating Blank Configuration...")
                
                self.appliances = [Appliance(**appliance) for appliance in fileData["appliances"]]

                for i in range(len(self.appliances)):
                    self.appliances[i].controls = [Control(**control) for control in fileData["appliances"][i]["controls"]]
        except FileNotFoundError:
            print("No controller configuration found! Creating Blank Configuration...")
        except json.JSONDecodeError:
            print("Invalid JSON - Creating New Configuration!")

def generate_base_appliance(name):
    """
    Generates a base appliance with default values
    """
    controls = []
    for i in range(6):
        # Add basic controls
        control = Control(f"Control {i+1}", 55, [0, 0, 255])
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
