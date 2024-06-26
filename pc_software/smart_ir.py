"""
Graphical User Interface for the Smart-Ir: Universal Remote Control System
Written by AB
"""
import struct
import sys
import os
import platform
import datetime as dt
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (
    QDialog,
    QApplication,
    QLabel,
    QMainWindow,
    QComboBox,
    QPushButton,
    QTextEdit,
    QStatusBar,
    QRadioButton,
    QColorDialog,
    QCheckBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QCoreApplication, QThread
import paho.mqtt.client as mqtt
import time
import numpy as np
import serial
import serial.tools.list_ports
import json
from datetime import datetime, timedelta
import threading
import pc_pb2
from smart_ir_data import Control, Appliance, ControllerConfig, VERSION, generate_base_appliance, orientation_to_string, action_from_control
from smart_ir_data import ORIENTATION_DOWN, ORIENTATION_LEFT, ORIENTATION_RIGHT, ORIENTATION_UP, ADDR_BOOK, CONTRACT_ADDR, CONTRACT_ABI, PC_ADDR
from mqtt_handler import MqttHandler
from web3 import Web3, HTTPProvider
from google.protobuf.message import DecodeError
from ab_util import formatIrCode   
from solcx import compile_source, compile_standard
import solcx
import argparse
import queue

# Configure command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--redeploy", dest = "redeploy", nargs="?", const = True, default = False, help = "Redeploys the solidity smart contract")
args = parser.parse_args()
print("Command line args:")
print("Redeploy: " + str(args.redeploy))

# Global Variables
portScanningState = False
connectionStatus = 1  # 1 represent no connection; 2 represent connected sucessfully; 3 represent disconnect manually
BASE_PATH = os.path.dirname(__file__)
MQTT_BROKER_HOSTNAME = "192.168.1.33"
FIRST_LAUNCH = True if args.redeploy else False
BLOCKCHAIN_UPDATE_INTERVAL = 2
sysControlQueue = queue.Queue()
RELOADING_CONFIG = False

class BlockchainHandler(QThread):
    """
    Handles PC Software Blockchain interactions
    """
    isConnected: bool
    updateGUI = pyqtSignal()
    contractDeployed = pyqtSignal()
    activityStr: str

    def __init__(self, firstLaunch: bool, contractAddr, contractAbi):
        super().__init__()
        # Setup Blockchain
        self.w3 = Web3(HTTPProvider("http://localhost:8545"))
        self.contractAddr = contractAddr
        self.contractAbi = contractAbi

        # Check if connected
        if not self.w3.is_connected():
            self.isConnected = False
            raise Exception("Unable to connect to Ethereum node")
        else:
            print("Blockchain Connected!")
            self.isConnected = True

        # Setup PC Account
        self.account = self.w3.eth.account.from_key(PC_ADDR.key)

        if firstLaunch:
            # Deploy the smart contract
            with open(os.path.join(BASE_PATH, "SmartIrContract.sol", "SmartIrContract.sol"), 'r') as file:
                fileContent = file.read()

                # Since this is a tesnet, it makes sense to dynamically deploy the contract
                # On a public net though, you would want to have a single contract and just do auth checks for getting data.

                # Compile the contract
                compiledSol = compile_source(fileContent, output_values=['abi', 'bin'])
                contractId, contractInterface = compiledSol.popitem()

                # get bytecode / bin
                bytecode = contractInterface['bin']

                # get abi
                abi = contractInterface['abi']
                contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

                # Deploy contract
                transaction  = contract.constructor().build_transaction(({
                    'chainId': 2002,  # Update with appropriate chain ID (e.g., 1 for mainnet, 3 for Ropsten)
                    'gas': 2000000,
                    'gasPrice': self.w3.to_wei('50', 'gwei'),
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                }))
                signed_tx = self.w3.eth.account.sign_transaction(transaction , PC_ADDR.key)

                # Send transaction
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                self.contractAddr = tx_receipt.contractAddress
                self.contractAbi = abi
                print(f"Updated Contract Address: {tx_receipt.contractAddress}")

        self.contract = self.w3.eth.contract(address=self.contractAddr, abi=self.contractAbi)
        self.activityStr = "---------------\n"

    def get_abi(self):
        """
        Returns the current contract abi
        """
        return self.contractAbi
    
    def get_addr(self): 
        """
        Returns the current contract address
        """
        return self.contractAddr

    def run(self):
        """
        Runs on thread startup
        """
        # Check that there is a valid blockchain connected
        if not self.isConnected:
            return
        
        while True:
            # Scan the blockchain every 5 seconds to fetch any new actions that have been executed
            latestBlock = self.w3.eth.block_number
            fromBlock = 0  # Scan the last 100 blocks
            toBlock = latestBlock
            self.eventFilterActionAdded = self.contract.events.IRActionAdded.create_filter(fromBlock=fromBlock, toBlock=toBlock)
            self.eventFilterSysControl = self.contract.events.SystemControlAdded.create_filter(fromBlock=fromBlock, toBlock=toBlock)
            self.activityStr = "---------------\n" # Clear activity string
            # We want to skip all the 
            for event in self.eventFilterActionAdded.get_all_entries():
                # Handler the block
                self.handle_ir_action_event(event)
            self.updateGUI.emit()

            if not sysControlQueue.empty():
                item = sysControlQueue.get()
                self.submit_system_control(item[0], item[1], item[2], item[3])

            time.sleep(BLOCKCHAIN_UPDATE_INTERVAL)
    
    def handle_ir_action_event(self, event, printActivity=False):
        """
        Handles incomming IR actions
        """
        # First get the timestamp and check if the timestamp is from the last 48hrs
        blockNumber = event['blockNumber']
        timestamp = self.w3.eth.get_block(blockNumber)["timestamp"]
        timestampDt = datetime.fromtimestamp(timestamp)
        timeDelta = timedelta(hours=48)
        now = datetime.now()

        # This transaction is old, don't display it
        if ((timestampDt - now) > timeDelta):
            return

        # Print Activity
        prettyTimestamp = timestampDt.strftime('%Y-%m-%d %H:%M:%S')
        self.activityStr = self.activityStr + f"Timestamp: {prettyTimestamp}\n"
        self.activityStr = self.activityStr + f"Block Number: {event['blockNumber']}\n"
        self.activityStr = self.activityStr + f"Transaction Hash: {event['transactionHash'].hex()}\n"
        self.activityStr = self.activityStr + f"Controller: {event['args']['controller']}\n"
        self.activityStr = self.activityStr + f"Transmitter: {event['args']['transmitter']}\n"
        self.activityStr = self.activityStr + f"Action: {event['args']['action']}\n"
        self.activityStr = self.activityStr + f"IR Code: {event['args']['irCode']}\n"
        self.activityStr = self.activityStr + "---------------\n"
        if printActivity:
            print(self.activityStr)
    
    def submit_system_control(self, parentAction, disabled, timeout, timeoutAction):
        """
        Subits system control requests to the blockchain
        """
        # Build the transaction
        print(f"Adding System Control: parentAction: {parentAction}, disabled: {disabled}, timeout: {timeout}, timeoutAction: {timeoutAction}")
        transaction = self.contract.functions.addSystemControl(parentAction, disabled, timeout, timeoutAction).build_transaction({
            'from': PC_ADDR.account,
            'nonce': self.w3.eth.get_transaction_count(PC_ADDR.account),
            'gas': 2000000,
            'gasPrice': self.w3.to_wei('1', 'gwei')
        })

        # Sign the transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=PC_ADDR.key)

        # Send the transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print the transaction receipt
        print(f'Transaction successful with hash: {tx_hash.hex()}')

class MainWindow(QMainWindow):
    """
    Main PC Software application
    """
    # Class Private Variables
    configData: ControllerConfig
    currentApplianceIndex: int
    currentControlIndex: int
    availableOrientations: list
    currentOrientationIndex: int
    irCodeStr: str

    def __init__(self):
        super(MainWindow, self).__init__()

        # Load in the UI File
        loadUi(os.path.abspath(os.path.join(BASE_PATH, "ui", "mainScreenUI.ui")), self)
        
        # Init Data
        print(BASE_PATH)
        self.configData = ControllerConfig(VERSION, [], ADDR_BOOK, CONTRACT_ADDR, CONTRACT_ABI)
        # Load configuration data
        readConfig = self.configData.load_from_disk()
        self.currentApplianceIndex = -1 # Not selected
        self.currentControlIndex = -1 # Not selected
        self.availableOrientations = [ORIENTATION_UP, ORIENTATION_RIGHT, ORIENTATION_DOWN, ORIENTATION_LEFT] # All 4 orientations are available to start with
        self.currentOrientationIndex = -1
        self.irCodeStr = ''

        if readConfig:
            # The config file was not found, assume first launch
            global FIRST_LAUNCH
            FIRST_LAUNCH = True

        # Initialise UI Elements
        self.port_select_c = self.findChild(QComboBox, "PortSelect_C")
        self.status = self.findChild(QLabel, "status")
        self.status_bar = self.findChild(QStatusBar, "statusBar")
        self.scanPortsB = self.findChild(QPushButton, "ScanPorts_B")
        self.portSelectorC = self.findChild(QComboBox, "PortSelector_C")
        self.connectB = self.findChild(QPushButton, "connectB")
        self.addApplianceB = self.findChild(QPushButton, "applianceAdd_b")
        self.addApplianceNameT = self.findChild(QTextEdit, "applianceNameAdd_t")
        self.updateControllersB = self.findChild(QPushButton, "updateControllers_b")
        self.selectedApplianceC = self.findChild(QComboBox, "selectedAppliance_c")
        self.controlLabelT = self.findChild(QTextEdit, "controlLabel_t")
        self.irCodeT = self.findChild(QTextEdit, "irCode_t")
        self.colourSelectB = self.findChild(QPushButton, "colourSelector_b")
        self.orientationC = self.findChild(QComboBox, "orientation_c")
        self.deleteApplianceB = self.findChild(QPushButton, "delAppliance_b")
        self.controlB_1 = self.findChild(QPushButton, "control1_B")
        self.controlB_2 = self.findChild(QPushButton, "control2_B")
        self.controlB_3 = self.findChild(QPushButton, "control3_B")
        self.controlB_4 = self.findChild(QPushButton, "control4_B")
        self.controlB_5 = self.findChild(QPushButton, "control5_B")
        self.controlB_6 = self.findChild(QPushButton, "control6_B")
        self.blockchainActivityT = self.findChild(QTextEdit, "blockchainActivity_t")
        self.irCodeHistoryT = self.findChild(QTextEdit, "irCodeHistory_t")
        self.parentalCheckbox = self.findChild(QCheckBox, "disableControl_cb")
        self.timeoutT = self.findChild(QTextEdit, "timeout_t")
        self.timeoutActionT = self.findChild(QTextEdit, "timeoutAction_t")

        # Configure Buttons 
        self.connectB.clicked.connect(self.connect_to_port)
        self.scanPortsB.clicked.connect(self.serial_scan_handler)
        self.addApplianceB.clicked.connect(self.add_appliance)
        self.controlB_1.clicked.connect(lambda: self.control_selected(0))
        self.controlB_2.clicked.connect(lambda: self.control_selected(1))
        self.controlB_3.clicked.connect(lambda: self.control_selected(2))
        self.controlB_4.clicked.connect(lambda: self.control_selected(3))
        self.controlB_5.clicked.connect(lambda: self.control_selected(4))
        self.controlB_6.clicked.connect(lambda: self.control_selected(5))
        self.selectedApplianceC.activated.connect(self.on_change_appliance)
        self.controlLabelT.textChanged.connect(self.on_control_label_changed)
        self.colourSelectB.clicked.connect(self.select_control_colour)
        self.orientationC.activated.connect(self.on_change_orientation)
        self.updateControllersB.clicked.connect(self.update_controllers)
        self.deleteApplianceB.clicked.connect(self.on_delete_appliance)
        self.irCodeT.textChanged.connect(self.on_ircode_set)
        self.parentalCheckbox.stateChanged.connect(self.on_update_parental_controls)
        self.timeoutT.textChanged.connect(self.on_update_parental_controls)
        self.timeoutActionT.textChanged.connect(self.on_update_parental_controls)

        # Serial Port Connection Timers
        self.connection_timer = QTimer(self)
        self.connection_timer.setSingleShot(False)
        self.connection_timer.timeout.connect(self.connection_info_update)
        self.connection_timer.start(100)

        self.serial_rcv_timer = QTimer(self)
        self.serial_rcv_timer.setSingleShot(False)
        self.serial_rcv_timer.timeout.connect(self.fetch_serial)
        self.serial_rcv_timer.start(10)

        # Multi-thread Handling using a Signaller
        self.signaller = Signaller()
        self.signaller.port_scan_complete.connect(self.update_ports_list)

        # Blockchain Handler
        self.blockchainHandler = BlockchainHandler(FIRST_LAUNCH, self.configData.smartIrContractAddress, self.configData.smartIrContractAbi)
        self.blockchainHandler.updateGUI.connect(self.update_blockchain_activity)
        self.blockchainHandler.contractDeployed.connect(self.contract_deployed)
        self.blockchainHandler.start()

        if FIRST_LAUNCH:
            self.contract_deployed()

        # Graceful Close
        QCoreApplication.instance().aboutToQuit.connect(self.close_window)

        # Load in Application Data
        self.reload_configuration_data()

    def add_appliance(self):
        """
        Adds an appliance to the system
        """
        # Get the appliance name
        name = self.addApplianceNameT.toPlainText()
        if name == "":
            print("No Appliance Name Set!")
            return
        
        if len(self.configData.appliances) >= 4:
            print("Appliance Limit Reached!")
            return

        # Create the appliance
        self.configData.appliances.append(generate_base_appliance(name))
        self.addApplianceNameT.clear()
        self.currentApplianceIndex = len(self.configData.appliances) - 1 # index's are 0-based
        self.currentControlIndex = -1

        # Refresh UI
        self.reload_configuration_data(applianceIndex=self.currentApplianceIndex)

    def on_change_appliance(self):
        """
        Updates the selected appliance
        """
        self.currentApplianceIndex = self.selectedApplianceC.currentIndex()
        self.currentControlIndex = -1

        # Reload
        self.reload_configuration_data(applianceIndex=self.currentApplianceIndex)

    def clear_fields(self):
        """
        Clear fields
        """
        # Save the state of the index selections before clearing
        appIdx = self.currentApplianceIndex
        conIdx = self.currentControlIndex
        self.currentApplianceIndex = -1
        self.currentControlIndex = -1
        self.controlLabelT.clear()
        self.irCodeT.clear()
        self.orientationC.clear()
        self.selectedApplianceC.clear()
        self.currentApplianceIndex = appIdx
        self.currentControlIndex = conIdx
        self.parentalCheckbox.setChecked(False)

    def reload_configuration_data(self, applianceName=None, applianceIndex=None, controlIndex=None):
        """
        Reload the configuration currently stored in memory into the GUI
        Can be used to reload the GUI configuration file after a major change has been made (such as adding a profile).
        NOTE: you should provide either an applianceName or applianceIndex to restore the existing state of the application.
              If both are provided the profile_name will be used by default.
        """
        global RELOADING_CONFIG
        RELOADING_CONFIG = True
        data = self.configData

        # Flush the latest configuration to disk
        data.save_to_disk()

        # Set appliance state
        if applianceName is not None:
            # Set this profile to the current selection
            index = 0
            for appliance in data.appliances:
                if appliance.name == applianceName:
                    index = data.appliances.index(appliance)
            self.currentApplianceIndex = index
        elif applianceIndex is not None:
            self.currentApplianceIndex = applianceIndex
        elif controlIndex is not None:
            self.currentControlIndex = controlIndex
        else:
            self.currentApplianceIndex = 0

        # Re-Populate GUI Fields
        # Appliance Selector
        self.clear_fields()
        if len(data.appliances) > 0:
            appIdx = self.currentApplianceIndex
            self.selectedApplianceC.clear() # This will trigger change_selected_appliance() which will clear all fields & reset the appliance drop down. Overwrite this
            # self.currentApplianceIndex = appIdx
            for i in range(len(data.appliances)):
                self.selectedApplianceC.addItem(data.appliances[i].name)
            self.currentApplianceIndex = appIdx # same as above, adding items technically clears the UI.
            self.selectedApplianceC.setCurrentIndex(appIdx)
            
            # Appliance Global Settings
            # Set orientation box based on available orientations
            self.orientationC.clear()
            for orientation in self.availableOrientations:
                self.orientationC.addItem(orientation_to_string(orientation))
            self.orientationC.setCurrentIndex(self.configData.appliances[self.currentApplianceIndex].orientation)
            
            # Controls
            for idx, control in enumerate(data.appliances[self.currentApplianceIndex].controls):
                self.update_control_ui(idx, control.label, control.colour)
        
            # Control Fields
            if (self.currentControlIndex >= 0):
                # Populate the Fields
                self.controlLabelT.setPlainText(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].label)
                self.irCodeT.setPlainText(str(hex(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].irCode)))
                self.parentalCheckbox.setChecked(True if data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].disabled else False)
                self.timeoutT.setPlainText(str(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeout))
                self.timeoutActionT.setPlainText(str(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeoutAction))

        RELOADING_CONFIG = False

    def update_control_ui(self, index, label, colour):
        """
        Update the UI for a control based on the provided index, label & colour.
        NOTE: Controls are labelled 1-6, corresponding indexes are 0-based i.e 0-5
        """
        colourStr = f"rgb({colour[0]}, {colour[1]}, {colour[2]})"
        styleSheet = f"border-radius:20px; background-color: {colourStr}; font: 75 12pt 'MS Shell Dlg 2';"
        self.colourSelectB.setStyleSheet(styleSheet)
        if index == 0:
            self.controlB_1.setStyleSheet(styleSheet)
            self.controlB_1.setText(label)
        elif index == 1:
            self.controlB_2.setStyleSheet(styleSheet)
            self.controlB_2.setText(label)
        elif index == 2:
            self.controlB_3.setStyleSheet(styleSheet)
            self.controlB_3.setText(label)
        elif index == 3:
            self.controlB_4.setStyleSheet(styleSheet)
            self.controlB_4.setText(label)
        elif index == 4:
            self.controlB_5.setStyleSheet(styleSheet)
            self.controlB_5.setText(label)
        elif index == 5:
            self.controlB_6.setStyleSheet(styleSheet)
            self.controlB_6.setText(label)

    def control_selected(self, idx):
        """
        Executes when a device control is selected
        """
        # Set selected index
        if self.currentApplianceIndex != -1 and len(self.configData.appliances) > 0:
            self.currentControlIndex = idx
            print(f"Control Selected: {self.configData.appliances[self.currentApplianceIndex].controls[idx].label}")
            
            # Reload the configuration
            self.reload_configuration_data(controlIndex=self.currentControlIndex)

    def on_control_label_changed(self):
        """
        Updates the control label
        """
        if self.currentControlIndex != -1:
            self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].label = self.controlLabelT.toPlainText()
            self.update_control_ui(self.currentControlIndex, self.controlLabelT.toPlainText(), self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].colour)

    def select_control_colour(self):
        """
        Updates the control colour
        """
        if self.currentControlIndex != -1:
            colour = QColorDialog.getColor()
            if (colour.isValid()):
                rgb = [colour.red(), colour.green(), colour.blue()]
                print("Selected Color:", rgb)
                label = self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].label
                self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].colour = rgb
                self.update_control_ui(self.currentControlIndex, label, rgb)

    def on_change_orientation(self):
        """
        Updates the selected orientation
        """
        if self.currentApplianceIndex != -1:
            print("Updating Orientation")
            self.configData.appliances[self.currentApplianceIndex].orientation = self.orientationC.currentIndex()
            self.currentOrientationIndex = self.orientationC.currentIndex()
            # TODO: add a check somewhere (likely when pressing update controllers that ensures each appliance has a different direction)

            self.reload_configuration_data(applianceIndex=self.currentApplianceIndex)

    def on_delete_appliance(self):
        """
        Deletes an appliance
        """
        if (self.currentApplianceIndex != -1 and len(self.configData.appliances) >= 1):
            self.configData.appliances.pop(self.currentApplianceIndex)
            
            # Reset indexes
            if len(self.configData.appliances) == 0:
                self.currentApplianceIndex = -1
            self.currentControlIndex = -1
            self.reload_configuration_data()

    def on_ircode_set(self):
        """
        Sets an IR code
        """
        # Check that a control is selected
        if self.currentControlIndex != -1:
            # Check that user has entered the correct number of characters
            enteredCode = self.irCodeT.toPlainText()
            if (len(enteredCode) == 10 or len(enteredCode) == 18) and enteredCode[0:2] == "0x":
                # Valid hex length & prefix - attempt to convert to unsigned int
                try:
                    uintVal = int(enteredCode, 0)
                    print(f"Setting IRCode Uint: {uintVal}")
                    self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].irCode = uintVal
                except ValueError:
                    print("Could not save IR Code!")

    def on_update_parental_controls(self):
        """
        Updaptes parental controls
        """
        if self.currentControlIndex != -1 and not RELOADING_CONFIG:
            try:
                disabled = 1 if self.parentalCheckbox.isChecked() else 0
                self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeout = int(self.timeoutT.toPlainText())
                self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeoutAction = int(self.timeoutActionT.toPlainText())
                self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].disabled = disabled
                timeout = self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeout
                timeoutAction = self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].timeoutAction
                if (timeoutAction >= 0 and timeoutAction <= 24):
                    sysControlQueue.put([action_from_control(self.currentControlIndex, self.currentApplianceIndex), self.parentalCheckbox.isChecked(), timeout, timeoutAction])
            except ValueError:
                print("Invalid parental control input provided!")

    def update_controllers(self):
        """
        Updates controller configurations
        """
        data = json.dumps(self.configData.to_dict(), indent=4,)
        print("Sending MQTT Message -")
        mqttWorker = MqttHandler("topic/gateway", MQTT_BROKER_HOSTNAME, str(data))
        mqttWorker.start()
        print(data)

    def update_blockchain_activity(self):
        """
        Updates blockchain activity box
        """
        self.blockchainActivityT.clear()
        self.blockchainActivityT.setPlainText(self.blockchainHandler.activityStr)
        self.blockchainActivityT.moveCursor(QTextCursor.End)

    def fetch_serial(self):
        """
        Fetch any pending serial data and process it accordingly
        """                        
        if (connectionStatus == 2):
            try:
                while self.ser.in_waiting:
                    # If there is data available on the serial line
                    buffer = self.ser.readline()
                    buffer = buffer[:-1] # Remove the \n

                    # Process the received message
                    message = pc_pb2.PCMessage()
                    message.ParseFromString(buffer)

                    # TODO: process messages
                    if message.cmd == pc_pb2.PCCommand.PC_CMD_IRCODE:
                        # IR Code Received
                        codeRcv = hex(message.irCode)
                        formattedCode = formatIrCode(codeRcv)
                        print(f"Code Received: {codeRcv}, Code Formatted:{formattedCode}")
                        self.irCodeStr = self.irCodeStr + f"{formattedCode}\n"
                        self.irCodeHistoryT.clear()
                        self.irCodeHistoryT.setPlainText(self.irCodeStr)
                        self.irCodeHistoryT.moveCursor(QTextCursor.End)
            except AttributeError:
                pass
            except DecodeError:
                print("Error parsing Packet!")

    def contract_deployed(self):
        print("Contract Redeployed!")
        self.configData.smartIrContractAbi = self.blockchainHandler.get_abi()
        self.configData.smartIrContractAddress = self.blockchainHandler.get_addr()
        self.configData.save_to_disk()
        self.update_controllers()

    def close_window(self):
        """
        Gracefully exits the application when the window is closed
        """
        # TODO: close comport
        pass

    def serial_scan_handler(self):
        """
        Createes a thread to handle port scanning and disconnect handling
        """
        # create thread for port scanning
        global portScanningState
        global connectionStatus
        if (portScanningState is False) and (connectionStatus == 1): 
            # create a thread to scan the serial ports
            self.serial_port_scan()
        
    def serial_port_scan(self):
        """
        Scans the serial ports
        """
        global portScanningState
        if not portScanningState:
            port_scan_thread = threading.Thread(
                target=self.port_scan_thread, args=())
            port_scan_thread.start()
            portScanningState = True

    def disconnect_port(self):
        global connectionStatus
        if self.ser and self.ser.isOpen():
            self.ser.close()
            print("Disconnected from serial port")
            connectionStatus = 1  # connection is closed manually

    def port_scan_thread(self):
        """
        Thread to scan all com ports
        """
        self.scanPortsB.setText("Scanning")
        ports_list = list(serial.tools.list_ports.comports())
        self.signaller.port_scan_complete.emit(ports_list)
        global portScanningState  # update scan status after finishing
        self.scanPortsB.setText("Scan")
        portScanningState = False

    def connection_info_update(self):
        """
        Display connection status info to the user and update the connect button
        """
        global connectionStatus
        if connectionStatus == 2:
            self.status.setText("Connected!")
            self.connectB.setText("Disconnect")
        elif connectionStatus == 3:
            # Manual Override
            self.status.setText("Connected!")
            self.connectB.setText("Disconnect")
        else:
            self.status.setText("No device!")
            # If we are scanning Comports, don't change the label until we finish
            if not portScanningState:
                self.connectB.setText("Connect")
                self.ser = None
            
    def update_ports_list(self, ports_list):
        # if there is no port available then report the error
        if len(ports_list) <= 0:
            print("No device detected!")
        
        # add the port in the ports_list to the combobox
        self.portSelectorC.clear()
        for port in ports_list:
            self.portSelectorC.addItem(port.description)
    
    def connect_to_port(self):
        """
        Connected/Disconnect from a selected serial port
        """
        global connectionStatus

        # Handle the disconnection
        if (connectionStatus == 2):
            self.disconnect_port()
        elif connectionStatus == 1:
            self.current_serial_port_value = (self.portSelectorC.currentText())  # e.g. serial.comport
            self.current_serial_port_value = self.current_serial_port_value.split("(")[-1].split(")")[0]  # HACK: com port name string splitting
            # Linux Override
            osType = platform.system()
            print(f"Os: {osType}")
            if (osType != "Windows"):
                # This is a UNIX Based system - overwrite the serial port value
                self.current_serial_port_value = '/dev/ttyACM0'
            print(self.current_serial_port_value)

            try:
                self.ser = serial.Serial(
                    self.current_serial_port_value,
                    baudrate=115200,
                    bytesize=8,
                    timeout=12,
                    inter_byte_timeout=5,
                    stopbits=serial.STOPBITS_ONE,
                )
                print("Connected to", self.current_serial_port_value)
                connectionStatus = 2
            except serial.SerialException as e:
                print("Error:", e)
                connectionStatus = 1

        # update scan status after finishing
        global portScanningState
        portScanningState = False
    
class Signaller(QObject):
    port_scan_complete = pyqtSignal(list)

# Main Application
if __name__ == '__main__':
    try:
        # Install Solidity Compiler
        solcx.install_solc('0.8.25')
        solcx.set_solc_version('0.8.25')

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(os.path.abspath(os.path.join(BASE_PATH, "ui", "smart_ir_logo.png"))))
        main_window = MainWindow()
        main_window.setWindowTitle("Smart IR - Universal Remote Control")
        main_window.show()

        sys.exit(app.exec_())
    except RuntimeError:
        print("Quitting Application!")