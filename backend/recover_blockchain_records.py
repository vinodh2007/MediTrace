
import sqlite3
from pathlib import Path
import hmac

from blockchain_utils import get_blockchain_contract

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "meditrace.db"


def main():

    web3, contract = get_blockchain_contract()

    print("Connected to Ganache!")
    print("Chain ID:", web3.eth.chain_id)
    print("Contract:", contract.address)

    # Retrieve all MedicineRegistered events
    event = contract.events.MedicineRegistered

    try:
        logs = event.get_logs(
            from_block=0,
            to_block="latest"
        )
    except TypeError:
        logs = event.get_logs(
            fromBlock=0,
            toBlock="latest"
        )

    print("\nEvents found:", len(logs))

    connection = sqlite3.connect(DATABASE_PATH)

    try:

        recovered = 0

        for log in logs:

            args = log["args"]

            medicine_id = args["medicineId"]
            blockchain_hash = args["medicineHash"]

            transaction_hash = log["transactionHash"].hex()
            block_number = log["blockNumber"]

            row = connection.execute(
                """
                SELECT medicine_hash
                FROM medicines
                WHERE medicine_id = ?
                """,
                (medicine_id,)
            ).fetchone()

            if row is None:
                print("Medicine not found in SQLite:", medicine_id)
                continue

            database_hash = row[0]

            # Only recover when the database hash matches
            # the hash recorded in the blockchain event.
            if not hmac.compare_digest(
                database_hash.lower(),
                blockchain_hash.lower()
            ):
                print("Hash mismatch:", medicine_id)
                continue

            connection.execute(
                """
                UPDATE medicines
                SET transaction_hash = ?,
                    block_number = ?
                WHERE medicine_id = ?
                """,
                (
                    transaction_hash,
                    block_number,
                    medicine_id
                )
            )

            recovered += 1

            print("\nRecovered:", medicine_id)
            print("Transaction:", transaction_hash)
            print("Block:", block_number)

        connection.commit()

        print("\nRecovery completed!")
        print("Records updated:", recovered)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
