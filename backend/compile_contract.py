
from pathlib import Path
import json

from solcx import compile_standard, install_solc, set_solc_version

BASE_DIR = Path(__file__).resolve().parent.parent

CONTRACT_PATH = BASE_DIR / "contracts" / "MedicineTracker.sol"
OUTPUT_PATH = BASE_DIR / "backend" / "contract_artifact.json"

SOLC_VERSION = "0.8.20"

print("Installing Solidity compiler...")

install_solc(SOLC_VERSION)
set_solc_version(SOLC_VERSION)

# Read Solidity contract
with open(CONTRACT_PATH, "r", encoding="utf-8") as file:
    contract_source = file.read()

print("Compiling MedicineTracker.sol...")

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "MedicineTracker.sol": {
                "content": contract_source
            }
        },
        "settings": {
            # Use older EVM instructions for Ganache compatibility
            "evmVersion": "london",
            "optimizer": {
                "enabled": True,
                "runs": 200
            },
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "evm.bytecode"
                    ]
                }
            }
        }
    },
    solc_version=SOLC_VERSION
)

contract = compiled["contracts"]["MedicineTracker.sol"]["MedicineTracker"]

bytecode = contract["evm"]["bytecode"]["object"]

if not bytecode:
    raise RuntimeError("Contract bytecode is empty!")

artifact = {
    "abi": contract["abi"],
    "bytecode": bytecode
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(artifact, file, indent=4)

print("Compilation successful!")
print("EVM Version: London")
print("Bytecode length:", len(bytecode))
print("Artifact saved:", OUTPUT_PATH)
