# Blockchain Gateway Script for the Controllers
import threading
import time
import json
import paho.mqtt.client as mqtt
from web3 import Web3, exceptions
from smart_ir_data import ControllerConfig, VERSION, ADDR_BOOK, CONTROLLERS, TRANSMITTER, CONTRACT_ADDR, CONTRACT_ABI, PC_ADDR, TRANSMITTER_ADDR
from datetime import datetime, timedelta

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("topic/gateway")
        client.subscribe("topic/blockchain")

    else:
        print(f"Failed to connect, return code {reason_code}\n")

class ControllerGateway(threading.Thread):
    config: ControllerConfig

    def __init__(self, mqttBroker, mqttPort, mqttUsername, mqttPassword, web3ProviderAddr, contractAddress, contractAbi):
        super().__init__()
        self.mqttBroker = mqttBroker
        self.mqttPort = mqttPort
        self.mqttUsername = mqttUsername
        self.mqttPassword = mqttPassword
        self.web3ProviderAddr = web3ProviderAddr
        self.contractAddress = contractAddress
        self.contractAbi = contractAbi
        self.mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.web3 = Web3(Web3.HTTPProvider(web3ProviderAddr))
        self.contract = self.web3.eth.contract(address=self.contractAddress, abi=self.contractAbi)
        self.isRunning = False
        self.config = ControllerConfig(VERSION, [], ADDR_BOOK, CONTRACT_ADDR, CONTRACT_ABI)
        self.configReceived = False
        self.systemControlsProcessed = 0
        self.timeoutActionsProcessed = 0   
        self.irCode = 0

    def welcome(self):
        print("Welcome to the Smart IR Peripheral Gateway & Blockchain Interface!")
        print(f"MQTT Broker: {self.mqttBroker}")
        print(f"MQTT mqttPort: {self.mqttPort}")
        print(f"MQTT Username: {self.mqttUsername}")
        print(f"MQTT Password: {self.mqttPassword}")
        print(f"Web3 Provider: {self.web3ProviderAddr}")
        print(f"Smart IR Contract Address: {self.contractAddress}")

    def on_config_msg(self, client, userdata, msg):
        print(f"Received message on {msg.topic}: {msg.payload.decode()}")
        self.handle_config_msg(msg.payload.decode())

    def handle_config_msg(self, msg):
        # Save a copy of the configuration
        tmpConfig = ControllerConfig(VERSION, [], ADDR_BOOK, CONTRACT_ADDR, CONTRACT_ABI)
        tmpConfig.load_from_string(msg)
        data = json.loads(msg)
        
        # Check that the contracts addresses are the same
        print(f"Contract Address: {data['smartIrContractAddress']}")
        if self.config.smartIrContractAddress != data['smartIrContractAddress']:
            # Reconfigure the Smart Ir Contract
            self.contractAddress = data['smartIrContractAddress']
            self.contractAbi = data['smartIrContractAbi']
            print("Reconfigured Smart IR Contract!")
            print(f"Smart IR Contract Address: {self.contractAddress}")
            self.contract = self.web3.eth.contract(address=self.contractAddress, abi=self.contractAbi)

        # Save the config
        self.config.smartIrContractAddress = data['smartIrContractAddress']
        self.config = tmpConfig

        # Publish the received message to the "configuration" topic
        tmpConfig.smartIrContractAbi = ''  # Remove the ABI from the config before sending to the core2 devices (in order to conserve memory)
        self.mqttClient.publish("topic/configuration", msg)
        self.configReceived = True

    def on_blockchain_msg(self, client, userdata, msg):
        print(f"Received message on {msg.topic}: {msg.payload.decode()}")
        self.handle_blockchain_msg(msg.payload.decode())

    def handle_blockchain_msg(self, msg):
        # Process the blockchain message
        data = json.loads(msg)
        controller = CONTROLLERS[data["controllerId"] - 1]
        # Build the transaction
        transaction = self.contract.functions.addIRAction(controller.account, TRANSMITTER.account, data["action"], int(data["irCode"])).build_transaction({
            'from': controller.account,
            'nonce': self.web3.eth.get_transaction_count(controller.account),
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('1', 'gwei')
        })

        # Sign the transaction
        try:
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=controller.key)

            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for the transaction to be mined
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            # Print the transaction receipt
            print(f'Transaction successful with hash: {tx_hash.hex()}')
        except ValueError:
            print(f"Replacement Transaction Underpriced - wait for existing transaction to execute.")
        except exceptions.TimeExhausted:
            print(f"Transactions receipts are timing out! Wait for blockchain to process current transactions!")

    def run(self):
        self.isRunning = True
        self.mqttClient.on_connect = on_connect
        self.mqttClient.message_callback_add("topic/gateway", self.on_config_msg)
        self.mqttClient.message_callback_add("topic/blockchain", self.on_blockchain_msg)
        self.mqttClient.username_pw_set(self.mqttUsername, self.mqttPassword)
        self.mqttClient.connect(self.mqttBroker, self.mqttPort, 60)
        self.mqttClient.loop_start()
        self.welcome()

        while self.isRunning:
            # Scan the blockchain every 2 seconds to fetch any new actions that have been executed
            # Check transactions
            self.call_checkTimeouts()

            latestBlock = self.web3.eth.block_number
            fromBlock = 0  # Scan the last 100 blocks
            toBlock = latestBlock
            self.eventFilterSysControl = self.contract.events.SystemControlAdded.create_filter(fromBlock=fromBlock, toBlock=toBlock)
            self.eventFilterIRActionTimeouts = self.contract.events.IRActionTimeout.create_filter(fromBlock=fromBlock, toBlock=toBlock)
            self.activityStr = "System Controls Start\n---------------\n" # Clear activity string
            self.timeoutStr = "Timeout Actions Start\n---------------\n" # Clear activity string
            # We want to skip all the 
            for event in self.eventFilterSysControl.get_all_entries():
                # Handler the block
                if self.configReceived and len(self.config.appliances) > 0:
                    self.handle_system_control_event(event, True)
            self.activityStr = self.activityStr + "System Controls End\n"
            for event in self.eventFilterIRActionTimeouts.get_all_entries():
                if self.configReceived and len(self.config.appliances) > 0:
                    self.handle_ir_timeout_event(event)

            # Update controllers if required
            if (len(self.eventFilterSysControl.get_all_entries()) != self.systemControlsProcessed):
                print(self.activityStr)
                self.mqttClient.publish("topic/configuration", json.dumps(self.config.to_dict(), indent=4))
                self.systemControlsProcessed = len(self.eventFilterSysControl.get_all_entries())

            if (len(self.eventFilterIRActionTimeouts.get_all_entries()) != self.timeoutActionsProcessed):
                print(self.timeoutStr)
                print("Publishing " + "{\"IR\": " + str(self.irCode) + "}")
                self.mqttClient.publish("topic/ir", ("{\"IR\": " + str(self.irCode) + "}"))
                self.timeoutActionsProcessed = len(self.eventFilterIRActionTimeouts.get_all_entries())

            time.sleep(1)

    def handle_system_control_event(self, event, printActivity=False):
        # First get the timestamp and check if the timestamp is from the last 2hrs
        blockNumber = event['blockNumber']
        timestamp = self.web3.eth.get_block(blockNumber)["timestamp"]
        timestampDt = datetime.fromtimestamp(timestamp)
        timeDelta = timedelta(hours=2)
        now = datetime.now()

        # Enforce Transaction
        applianceIdx = (event['args']['parentAction'] // 6)
        applianceNum = (event['args']['parentAction'] // 6) * 6
        controlNum = event['args']['parentAction'] % 6
        self.config.appliances[applianceIdx].controls[controlNum - 1].disabled = event['args']['disabled']

        # This transaction is old, don't display it
        if ((timestampDt - now) > timeDelta):
            return

        # Print Activity
        prettyTimestamp = timestampDt.strftime('%Y-%m-%d %H:%M:%S')
        self.activityStr = self.activityStr + f"Timestamp: {prettyTimestamp}\n"
        self.activityStr = self.activityStr + f"Block Number: {event['blockNumber']}\n"
        self.activityStr = self.activityStr + f"Transaction Hash: {event['transactionHash'].hex()}\n"
        self.activityStr = self.activityStr + f"Parent Action: {event['args']['parentAction']}\n"
        self.activityStr = self.activityStr + f"Disabled: {event['args']['disabled']}\n"
        self.activityStr = self.activityStr + f"Timeout: {event['args']['timeout']}\n"
        self.activityStr = self.activityStr + f"Timeout Action: {event['args']['timeoutAction']}\n"
        self.activityStr = self.activityStr + "---------------\n"

    def handle_ir_timeout_event(self, event):
        # Transmit the appropriate action
        applianceIdx = (event['args']['timeoutAction'] // 6)
        applianceNum = (event['args']['timeoutAction'] // 6) * 6
        controlNum = event['args']['timeoutAction'] % 6
        self.irCode = self.config.appliances[applianceIdx].controls[controlNum - 1].irCode

        # Print Activity
        self.timeoutStr = self.timeoutStr + ("---------------\n")
        blockNumber = event['blockNumber']
        timestamp = self.web3.eth.get_block(blockNumber)["timestamp"]
        timestampDt = datetime.fromtimestamp(timestamp)
        prettyTimestamp = timestampDt.strftime('%Y-%m-%d %H:%M:%S')
        self.timeoutStr = self.timeoutStr + f"Timestamp: {prettyTimestamp}\n"
        self.timeoutStr = self.timeoutStr + f"Block Number: {event['blockNumber']}\n"
        self.timeoutStr = self.timeoutStr + f"Transaction Hash: {event['transactionHash'].hex()}\n"
        self.timeoutStr = self.timeoutStr + f"Parent Action: {event['args']['parentAction']}\n"
        self.timeoutStr = self.timeoutStr + f"Timeout Action: {event['args']['timeoutAction']}\n"
        self.timeoutStr = self.timeoutStr + f"Timeout: {event['args']['timeout']}\n"
        self.timeoutStr = self.timeoutStr + "---------------\n"     

    def stop(self):
        self.isRunning = False
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()
    
    def call_checkTimeouts(self):
        print("Checking Timeouts")
        # Build the transaction
        transaction = self.contract.functions.checkTimeouts().build_transaction({
            'from': TRANSMITTER_ADDR.account,
            'nonce': self.web3.eth.get_transaction_count(TRANSMITTER_ADDR.account),
            'gas': 2000000,  # Adjust the gas limit as necessary
            'gasPrice': self.web3.to_wei('20', 'gwei')  # Adjust the gas price as necessary
        })

        # Sign the transaction
        signed_txn = self.web3.eth.account.sign_transaction(transaction, TRANSMITTER_ADDR.key)

        # Send the transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for the transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"Transaction hash: {tx_hash.hex()}")
        # print(f"Transaction receipt: {tx_receipt}")

if __name__ == "__main__":
    # Configure Gateway
    mqttBroker = "localhost"
    mqttPort = 1883
    mqttUsername = "observer"
    mqttPassword = "csse4011"
    web3Provider = "http://localhost:8545"
    contractAddress = CONTRACT_ADDR
    contractAbi = CONTRACT_ABI

    gateway = ControllerGateway(mqttBroker, mqttPort, mqttUsername, mqttPassword, web3Provider, contractAddress, contractAbi)
    gateway.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()
