# Gets all of the actions registered to a Smart IR contract
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

contract_instance = w3.eth.contract(address=contractAddress, abi=abi)

value = contract_instance.functions.getActions().call()

print(value)