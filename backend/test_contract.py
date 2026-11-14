
from pathlib import Path
import json
import hashlib

from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent.parent

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not web3.is_connected():
    raise ConnectionError("Cannot connect to Ganache")

# Load deployed contract details
deployment_path = BASE_DIR / "backend" / "deployed_contract.json"

with open(deployment_path, "r", encoding="utf-8") as file:
    deployment = json.load(file)

contract_address = Web3.to_checksum_address(deployment["address"])

contract = web3.eth.contract(
    address=contract_address,
    abi=deployment["abi"]
)

account = web3.eth.accounts[0]

# Generate a sample SHA-256 hash
sample_data = "MediTrace Test Medicine"
medicine_hash = hashlib.sha256(
    sample_data.encode()
).hexdigest()

medicine_id = "MED-TEST001"

print("Connected to Ganache!")
print("Contract:", contract_address)

# Register sample medicine on blockchain
print("\nRegistering test medicine...")

tx_hash = contract.functions.registerMedicine(
    medicine_id,
    medicine_hash
).transact({
    "from": account,
    "gas": 300000
})

receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

if receipt.status != 1:
    raise RuntimeError("Blockchain registration failed")

print("Medicine stored successfully!")
print("Transaction:", tx_hash.hex())

# Verify medicine
result = contract.functions.verifyMedicine(
    medicine_id,
    medicine_hash
).call()

print("\nVerification result:", result)

# Retrieve medicine
details = contract.functions.getMedicine(
    medicine_id
).call()

print("\nMedicine details:")
print("Medicine ID:", details[0])
print("Medicine Hash:", details[1])
print("Registered By:", details[2])
print("Timestamp:", details[3])
print("Exists:", details[4])
