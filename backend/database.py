
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "meditrace.db"


def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# Create or update database
def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            medicine_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            batch_id TEXT UNIQUE NOT NULL,

            manufacturer TEXT NOT NULL,

            manufacturing_date TEXT NOT NULL,

            expiry_date TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            medicine_hash TEXT,

            digital_signature TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Add cryptography columns to older databases
    columns = {
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(medicines)"
        ).fetchall()
    }

    if "medicine_hash" not in columns:

        cursor.execute("""
            ALTER TABLE medicines
            ADD COLUMN medicine_hash TEXT
        """)

    if "digital_signature" not in columns:

        cursor.execute("""
            ALTER TABLE medicines
            ADD COLUMN digital_signature TEXT
        """)

    
    if "transaction_hash" not in columns:

        cursor.execute("""
            ALTER TABLE medicines
            ADD COLUMN transaction_hash TEXT
        """)

    if "block_number" not in columns:

        cursor.execute("""
            ALTER TABLE medicines
            ADD COLUMN block_number INTEGER
        """)


    connection.commit()

    connection.close()


# Save medicine with hash and signature

# Save medicine with hash, signature and blockchain details
def add_medicine(
    medicine_id,
    name,
    batch_id,
    manufacturer,
    manufacturing_date,
    expiry_date,
    quantity,
    medicine_hash,
    digital_signature,
    transaction_hash=None,
    block_number=None
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO medicines (

                medicine_id,
                name,
                batch_id,
                manufacturer,
                manufacturing_date,
                expiry_date,
                quantity,
                medicine_hash,
                digital_signature,
                transaction_hash,
                block_number

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            medicine_id,
            name,
            batch_id,
            manufacturer,
            manufacturing_date,
            expiry_date,
            quantity,
            medicine_hash,
            digital_signature,
            transaction_hash,
            block_number

        ))

        connection.commit()

    finally:

        connection.close()


# Retrieve medicine by ID
def get_medicine(medicine_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM medicines
        WHERE medicine_id = ?
    """, (medicine_id,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return dict(result)
