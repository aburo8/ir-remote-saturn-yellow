from web3 import Web3, HTTPProvider

# Connect to an Ethereum node
web3 = Web3(HTTPProvider("http://localhost:8545"))

# Replace with your contract's ABI and address
contract_abi = '''
[
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
				"internalType": "uint256",
				"name": "timeoutAction",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timeout",
				"type": "uint256"
			}
		],
		"name": "IRActionTimeout",
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
		"name": "checkTimeouts",
		"outputs": [],
		"stateMutability": "nonpayable",
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
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
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
contract_address = '0x6D0a2A4501cbd0DEF6fE15B4932fa02F6118b787'

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to handle events and print them
def handle_event(event):
    print(f"Event: {event.event}")
    print(f"Args: {event.args}")

# Asynchronous event listener
from web3.middleware import geth_poa_middleware
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

import asyncio

async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

# Function to create event filters and start the log loop
def main():
    # Create event filters
    ir_action_added_filter = contract.events.IRActionAdded.create_filter(fromBlock='latest')
    system_control_added_filter = contract.events.SystemControlAdded.create_filter(fromBlock='latest')
    ir_action_timeout_filter = contract.events.IRActionTimeout.create_filter(fromBlock='latest')

    # Start the log loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(ir_action_added_filter, 2),
                log_loop(system_control_added_filter, 2),
                log_loop(ir_action_timeout_filter, 2)
            )
        )
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
