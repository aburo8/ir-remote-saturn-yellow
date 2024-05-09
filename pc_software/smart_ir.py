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
from PyQt5.QtWidgets import (
    QDialog,
    QApplication,
    QLabel,
    QMainWindow,
    QComboBox,
    QPushButton,
    QTextEdit,
    QStatusBar,
    QRadioButton
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QCoreApplication, QThread
import paho.mqtt.client as mqtt
import time
import numpy as np
import serial
import serial.tools.list_ports
import json
from datetime import datetime
import threading
import pc_pb2
from smart_ir_data import Control, Appliance, ControllerConfig, VERSION, generate_base_appliance

# Global Variables
portScanningState = False
connectionStatus = 1  # 1 represent no connection; 2 represent connected sucessfully; 3 represent disconnect manually

class MainWindow(QMainWindow):
    # Class Private Variables
    configData: ControllerConfig
    currentApplianceIndex: int
    currentControlIndex: int

    def __init__(self):
        super(MainWindow, self).__init__()

        # Load in the UI File
        loadUi(os.path.abspath("pc_software/ui/mainScreenUI.ui"), self)
        
        # Init Data
        self.configData = ControllerConfig(VERSION, [])
        self.currentApplianceIndex = -1 # Not selected
        self.currentControlIndex = -1 # Not selected

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
        self.selectedApplianceC.activated.connect(self.change_selected_appliance)
        self.controlLabelT.textChanged.connect(self.on_control_label_changed)

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

        # Graceful Close
        QCoreApplication.instance().aboutToQuit.connect(self.close_window)

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

    def change_selected_appliance(self):
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
        self.currentApplianceIndex = appIdx
        self.currentControlIndex = conIdx

    def reload_configuration_data(self, applianceName=None, applianceIndex=None, controlIndex=None):
        """
        Reload the configuration currently stored in memory into the GUI
        Can be used to reload the GUI configuration file after a major change has been made (such as adding a profile).
        NOTE: you should provide either an applianceName or applianceIndex to restore the existing state of the application.
              If both are provided the profile_name will be used by default.
        """
        data = self.configData
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
        else:
            self.currentApplianceIndex = 0

        # Re-Populate GUI Fields
        # Appliance Selector
        self.clear_fields()
        if len(data.appliances) > 0:
            appIdx = self.currentApplianceIndex
            self.selectedApplianceC.clear() # This will trigger change_selected_appliance() which will clear all fields & reset the appliance drop down. Overwrite this
            self.currentApplianceIndex = appIdx
            for i in range(len(data.appliances)):
                self.selectedApplianceC.addItem(data.appliances[i].name)
                self.currentApplianceIndex = appIdx # same as above, adding items technically clears the UI.

            self.selectedApplianceC.setCurrentIndex(appIdx)
            # Appliance Global Settings
            self.orientationC.setCurrentIndex(data.appliances[self.currentApplianceIndex].orientation)
        
            # Controls
            for idx, control in enumerate(data.appliances[self.currentApplianceIndex].controls):
                self.update_control_ui(idx, control.label, control.colour)
        
            # Control Fields
            if (self.currentControlIndex >= 0):
                # Populate the Fields
                self.controlLabelT.setPlainText(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].label)
                self.irCodeT.setPlainText(str(data.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].irCode))

    def update_control_ui(self, index, label, colour):
        """
        Update the UI for a control based on the provided index, label & colour.
        NOTE: Controls are labelled 1-6, corresponding indexes are 0-based i.e 0-5
        """
        colourStr = f"rgb({colour[0]}, {colour[1]}, {colour[2]})"
        styleSheet = f"border-radius:20px; background-color: {colourStr}; font: 75 12pt 'MS Shell Dlg 2';"
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
        if self.currentApplianceIndex != -1:
            self.currentControlIndex = idx
            print(f"Control Selected: {self.configData.appliances[self.currentApplianceIndex].controls[idx].label}")
            
            # Reload the configuration
            self.reload_configuration_data(applianceIndex=self.currentApplianceIndex)

    def on_control_label_changed(self):
        if self.currentControlIndex != -1:
            self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].label = self.controlLabelT.toPlainText()
            self.update_control_ui(self.currentControlIndex, self.controlLabelT.toPlainText(), self.configData.appliances[self.currentApplianceIndex].controls[self.currentControlIndex].colour)
        else:
            print("No Label Selected!")

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
            except AttributeError:
                pass
            except DecodeError:
                print("Error parsing Packet!")

    def close_window(self):
        """
        Gracefully exits the application when the window is closed
        """
        self.us_thread.quit()

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
            if (platform.system != "Windows"):
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
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.setWindowTitle("Smart IR - Universal Remote Control")
main_window.show()

try:
    sys.exit(app.exec_())
except RuntimeError:
    print("Quitting Application!")
