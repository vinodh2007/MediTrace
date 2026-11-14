
import json
from pathlib import Path

from web3 import Web3


BASE_DIR = Path(__file__).resolve().parent.parent

GANACHE_URL = "http://127.0.0.1:7545"

DEPLOYMENT_PATH = (
    BASE_DIR / "backend" / "deployed_contract.json"
)


def get_blockchain_contract():

    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

    if not web3.is_connected():
        raise ConnectionError("Cannot connect to Ganache")

    with open(DEPLOYMENT_PATH, "r", encoding="utf-8") as file:
        deployment = json.load(file)

    # Check that we are using the correct Ganache network
    if web3.eth.chain_id != deployment["chain_id"]:
        raise ConnectionError("Ganache Chain ID does not match deployment")

    contract_address = Web3.to_checksum_address(
        deployment["address"]
    )

    # Make sure contract exists at this address
    contract_code = web3.eth.get_code(contract_address)

    if not contract_code:
        raise ConnectionError("Smart contract not found on this network")

    contract = web3.eth.contract(
        address=contract_address,
        abi=deployment["abi"]
    )

    return web3, contract


def register_on_blockchain(medicine_id, medicine_hash):

    web3, contract = get_blockchain_contract()

    # Ganache's first unlocked account
    account = web3.eth.accounts[0]

    transaction_hash = contract.functions.registerMedicine(
        medicine_id,
        medicine_hash
    ).transact({
        "from": account,
        "gas": 300000
    })

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    if receipt.status != 1:
        raise RuntimeError("Blockchain registration failed")

    return {
        "transaction_hash": transaction_hash.hex(),
        "contract_address": contract.address,
        "block_number": receipt.blockNumber
    }


def verify_on_blockchain(medicine_id, medicine_hash):

    web3, contract = get_blockchain_contract()

    # Read the medicine record from Ethereum
    details = contract.functions.getMedicine(
        medicine_id
    ).call()

    exists = details[4]

    if not exists:
        return {
            "exists": False,
            "hash_matches": False
        }

    # Compare the supplied hash with the blockchain hash
    hash_matches = contract.functions.verifyMedicine(
        medicine_id,
        medicine_hash
    ).call()

    return {
        "exists": True,
        "hash_matches": hash_matches
    }
