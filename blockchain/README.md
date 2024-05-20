# Blockchain

Local blockchain development network, created using build developed by Prysm -

https://docs.prylabs.network/docs/advanced/proof-of-stake-devnet#using-our-newsly-created-devnet

See the `scripts` folder for utility scripts to assist with interacting with the network.

See the `test_contracts` folder for example begineer solidity contracts which explain the basic features of the language.

## Running the Blockchain

To run the blockchain, open the `eth-pos-devnet` directory and run the command `docker compose up -d`. Ensure docker is running and you have sufficient compute resources.

Additionally, to perform any Blockchain interactions with the controller/transmitter units, ensure that the Peripheral Gateway server script is running (*Note: that this is not built into the application*).