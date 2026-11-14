
from pathlib import Path
import json

from web3 import Web3

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = BASE_DIR / "backend" / "contract_artifact.json"
DEPLOYMENT_PATH = BASE_DIR / "backend" / "deployed_contract.json"

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not web3.is_connected():
    raise ConnectionError("Cannot connect to Ganache!")

print("Connected to Ganache!")
print("Chain ID:", web3.eth.chain_id)

# Use the first Ganache account
account = web3.eth.accounts[0]
print("Deploying from:", account)

# Load compiled contract
with open(ARTIFACT_PATH, "r", encoding="utf-8") as file:
    artifact = json.load(file)

# Create contract object
MedicineTracker = web3.eth.contract(
    abi=artifact["abi"],
    bytecode=artifact["bytecode"]
)

# Deploy smart contract
print("Deploying MedicineTracker contract...")

transaction_hash = MedicineTracker.constructor().transact({
    "from": account,
    "gas": 3000000
})

# Wait for deployment confirmation
receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

if receipt.status != 1:
    raise RuntimeError("Smart contract deployment failed!")

contract_address = receipt.contractAddress

# Save deployment details
deployment_data = {
    "address": contract_address,
    "abi": artifact["abi"],
    "chain_id": web3.eth.chain_id,
    "transaction_hash": transaction_hash.hex()
}

with open(DEPLOYMENT_PATH, "w", encoding="utf-8") as file:
    json.dump(deployment_data, file, indent=4)

print("\nSmart contract deployed successfully!")
print("Contract Address:", contract_address)
print("Transaction Hash:", transaction_hash.hex())
print("Deployment Block:", receipt.blockNumber)
print("Details saved to:", DEPLOYMENT_PATH)
