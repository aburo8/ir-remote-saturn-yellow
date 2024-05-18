# Script to create a new account to sign transactions with
from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider("http://localhost:8545"))

# Check if Web3 is connected
print("Testnet Connected -")
print(w3.is_connected())

acc = w3.eth.account.create()
print(f'private key={w3.to_hex(acc.key)}, account={acc.address}')

print(w3.eth.get_block('latest'))