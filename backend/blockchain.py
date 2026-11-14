
from web3 import Web3

GANACHE_URL = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

def connect_blockchain():
    if web3.is_connected():
        print("Connected to Ganache!")
        print("Chain ID:", web3.eth.chain_id)
        print("First account:", web3.eth.accounts[0])
        print("Latest block:", web3.eth.block_number)
    else:
        print("Connection failed!")

if __name__ == "__main__":
    connect_blockchain()
