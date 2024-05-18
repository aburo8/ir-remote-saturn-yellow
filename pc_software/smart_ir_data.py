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
class Account:
    """
    Account Information
    """
    name: str
    account: str
    key: str

PC_ADDR = Account(name='pc', account='0x00C928592E3635D542A8E5F7821439AAb6eF9B6D', key='0x52485d99ad13489881ee4be5fafa6bc88f8c886d2a41726e25f15f7c8ad993d8')
CONTROLLER1_ADDR = Account(name='controller1', account='0x64cD35b24D7c8d468dB3F2CfEb1D2B0E7963A261', key='0x33edf39c89424f6ecf026fc518e3c79df8687b609feacf56770cf5d8730faadf')
CONTROLLER2_ADDR = Account(name='controller2', account='0x4EAbe0426C3071dd4562feC540235B2De295c2e6', key='0xd729e6c926ae46a1e60ebe1112cdb4367c3ad8f52f9fbb34c636be083c972416')
TRANSMITTER_ADDR = Account(name='transmitter', account='0x4EAbe0426C3071dd4562feC540235B2De295c2e6', key='0xd729e6c926ae46a1e60ebe1112cdb4367c3ad8f52f9fbb34c636be083c972416')
ADDR_BOOK = [PC_ADDR, CONTROLLER1_ADDR, CONTROLLER2_ADDR, TRANSMITTER_ADDR]
CONTROLLERS = [CONTROLLER1_ADDR, CONTROLLER2_ADDR]
TRANSMITTER = TRANSMITTER_ADDR

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
    addressBook: List[Account]
    smartIrContractAddress: str
    smartIrContractAbi: str

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

    def load_from_string(self, data):
        fileData = json.loads(data)
        if self.version != fileData["version"]:
            print("Controller configuration outdated! Creating Blank Configuration...")
        
        self.appliances = [Appliance(**appliance) for appliance in fileData["appliances"]]

        for i in range(len(self.appliances)):
            self.appliances[i].controls = [Control(**control) for control in fileData["appliances"][i]["controls"]]

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

def rgb_to_hex(r, g, b):
    """
    Convert RGB values to hexadecimal format.
    """
    # Ensure RGB values are within valid range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    # Convert RGB to hexadecimal format
    hex_value = "0x{:02x}{:02x}{:02x}".format(r, g, b)
    return hex_value

CONTRACT_ADDR = "0x8BfC4B63Cb65d1004c9e9a0a8982915Dc9aAAf29"
CONTRACT_ABI = '''
[
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "controller",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "transmitter",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "action",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "irCode",
				"type": "uint256"
			}
		],
		"name": "addIRAction",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "parentAction",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "disabled",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "timeout",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "timeoutAction",
				"type": "uint256"
			}
		],
		"name": "addSystemControl",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "Unauthorized",
		"type": "error"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "controller",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "transmitter",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "action",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "irCode",
				"type": "uint256"
			}
		],
		"name": "IRActionAdded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "parentAction",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "bool",
				"name": "disabled",
				"type": "bool"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timeout",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timeoutAction",
				"type": "uint256"
			}
		],
		"name": "SystemControlAdded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "actions",
		"outputs": [
			{
				"internalType": "address",
				"name": "controller",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "transmitter",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "action",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "irCode",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "controls",
		"outputs": [
			{
				"internalType": "bool",
				"name": "disabled",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "timeout",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "timeoutAction",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getActions",
		"outputs": [
			{
				"components": [
					{
						"internalType": "address",
						"name": "controller",
						"type": "address"
					},
					{
						"internalType": "address",
						"name": "transmitter",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "action",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "irCode",
						"type": "uint256"
					}
				],
				"internalType": "struct SmartIR.IRAction[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
'''