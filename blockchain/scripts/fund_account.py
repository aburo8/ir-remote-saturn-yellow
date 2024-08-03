# Transfer funds between accounts
from web3 import Web3, HTTPProvider
from addr_book import controller1_addr, controller2_addr, pc_addr, transmitter_addr

# Change line 6 to fund different accounts
# TODO: Setup auto-refund (after transactions are complete the PC should reimburse the other accounts)
addrToFunc = transmitter_addr

w3 = Web3(HTTPProvider("http://localhost:8545"))

# Check if Web3 is connected
print("Testnet Connected -")
print(w3.is_connected())

# Note: Never commit your key in your code! Use env variables instead:
pk = addrToFunc["key"]

# Instantiate an Account object from your key:
acct2 = w3.eth.account.from_key(pk)

# For the sake of this example, fund the new account:
tx_hash = w3.eth.send_transaction({
    "from": "0x123463a4B065722E99115D6c222f267d9cABb524",
    "value": w3.to_wei(2000, 'ether'),
    "to": acct2.address
})

tx = w3.eth.get_transaction(tx_hash)
assert tx["from"] == "0x123463a4B065722E99115D6c222f267d9cABb524"