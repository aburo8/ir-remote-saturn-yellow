# Blockchain Gateway Script for the Controllers
import threading
import time
import json
import paho.mqtt.client as mqtt
from web3 import Web3
from smart_ir_data import ControllerConfig, VERSION, ADDR_BOOK, CONTROLLERS, TRANSMITTER

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
        self.config = ControllerConfig(VERSION, [], ADDR_BOOK)

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
        self.config.load_from_string(msg)

        # Publish the received message to the "configuration" topic
        self.mqttClient.publish("topic/configuration", msg)

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
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=controller.key)

        # Send the transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        # Print the transaction receipt
        print(f'Transaction successful with hash: {tx_hash.hex()}')

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
            time.sleep(1)

    def stop(self):
        self.isRunning = False
        self.mqttClient.loop_stop()
        self.mqttClient.disconnect()

if __name__ == "__main__":
    # Configure Gateway
    mqttBroker = "localhost"
    mqttPort = 1883
    mqttUsername = "observer"
    mqttPassword = "csse4011"
    web3Provider = "http://localhost:8545"
    contractAddress = "0x8BfC4B63Cb65d1004c9e9a0a8982915Dc9aAAf29"
    contractAbi = '''
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

    gateway = ControllerGateway(mqttBroker, mqttPort, mqttUsername, mqttPassword, web3Provider, contractAddress, contractAbi)
    gateway.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()
