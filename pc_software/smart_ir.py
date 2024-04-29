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

# Global Variables
portScanningState = False
connectionStatus = 1  # 1 represent no connection; 2 represent connected sucessfully; 3 represent disconnect manually

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Load in the UI File
        loadUi(os.path.abspath("pc_software/ui/mainScreenUI.ui"), self)

        # Initialise UI Elements
        self.port_select_c = self.findChild(QComboBox, "PortSelect_C")
        self.status = self.findChild(QLabel, "status")
        self.status_bar = self.findChild(QStatusBar, "statusBar")
        self.scanPortsB = self.findChild(QPushButton, "ScanPorts_B")
        self.portSelectorC = self.findChild(QComboBox, "PortSelector_C")
        self.connectB = self.findChild(QPushButton, "connectB")

        # Configure Buttons 
        self.connectB.clicked.connect(self.connect_to_port)
        self.scanPortsB.clicked.connect(self.serial_scan_handler)

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

        QCoreApplication.instance().aboutToQuit.connect(self.close_window)
        

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
