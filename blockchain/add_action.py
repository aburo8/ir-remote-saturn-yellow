
from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider("http://localhost:8545"))
# Gets all of the submitted IR Actions from a specified deployed contract instance
contractAddress = "0x8BfC4B63Cb65d1004c9e9a0a8982915Dc9aAAf29"
abi = '''
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

# Check if connected
if not w3.is_connected():
    raise Exception("Unable to connect to Ethereum node")

contract_instance = w3.eth.contract(address=contractAddress, abi=abi)

# Transaction parameters
transmitter_address = '0xD6C8ba6cABF5586fcc92826038b3385FF19Fc1B1'
action = 1  # Example action
ir_code = 123456  # Example IR code
my_address = "0x64cD35b24D7c8d468dB3F2CfEb1D2B0E7963A261"
private_key = "0x33edf39c89424f6ecf026fc518e3c79df8687b609feacf56770cf5d8730faadf"

# Build the transaction
transaction = contract_instance.functions.addIRAction(my_address, transmitter_address, action, ir_code).build_transaction({
    'from': my_address,
    'nonce': w3.eth.get_transaction_count(my_address),
    'gas': 2000000,
    'gasPrice': w3.to_wei('1', 'gwei')
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Wait for the transaction to be mined
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Print the transaction receipt
print(f'Transaction successful with hash: {tx_hash.hex()}')