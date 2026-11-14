from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template_string
)
from flask_cors import CORS
from pathlib import Path
from datetime import date, timedelta
import sqlite3
import hmac
import qrcode

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

BASE_FOLDER = Path(__file__).resolve().parent.parent
FRONTEND_FOLDER = BASE_FOLDER / "frontend"

QR_FOLDER = Path(__file__).resolve().parent / "qr_codes"
QR_FOLDER.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

from database import (
    initialize_database,
    add_medicine,
    get_medicine,
    get_connection
)


# --------------------------------------------------
# CRYPTOGRAPHY FUNCTIONS
# --------------------------------------------------

from crypto_utils import (
    load_or_create_keys,
    generate_hash,
    create_signature,
    verify_signature
)


# --------------------------------------------------
# BLOCKCHAIN FUNCTIONS
# --------------------------------------------------

from blockchain_utils import (
    register_on_blockchain,
    verify_on_blockchain,
    get_blockchain_contract
)


# --------------------------------------------------
# INITIALIZE DATABASE AND RSA KEYS
# --------------------------------------------------

initialize_database()

private_key, public_key = load_or_create_keys()


# --------------------------------------------------
# CONSISTENT MEDICINE INFORMATION
# --------------------------------------------------

def medicine_payload(record):

    return {
        "medicine_id": record["medicine_id"],
        "name": record["name"],
        "batch_id": record["batch_id"],
        "manufacturer": record["manufacturer"],
        "manufacturing_date": record["manufacturing_date"],
        "expiry_date": record["expiry_date"],
        "quantity": record["quantity"]
    }


# --------------------------------------------------
# MEDICINE AVAILABILITY
# --------------------------------------------------

def get_medicine_availability(quantity, expiry_date):

    try:
        expiry = date.fromisoformat(expiry_date)
    except (ValueError, TypeError):
        expiry = None

    if expiry is not None and expiry < date.today():
        return "Expired"

    if quantity <= 0:
        return "Out of Stock"

    if quantity <= 50:
        return "Low Stock"

    if expiry is not None and expiry <= date.today() + timedelta(days=30):
        return "Expiring Soon"

    return "Available"


# --------------------------------------------------
# HOMEPAGE
# --------------------------------------------------

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


# --------------------------------------------------
# REGISTRATION PAGE
# --------------------------------------------------

@app.route("/register")
def register_page():

    return send_from_directory(
        FRONTEND_FOLDER,
        "register.html"
    )


# --------------------------------------------------
# VERIFICATION PAGE
# --------------------------------------------------

@app.route("/verify")
def verify_page():

    return send_from_directory(
        FRONTEND_FOLDER,
        "verify.html"
    )


# --------------------------------------------------
# BLOCKCHAIN PAGE
# --------------------------------------------------

@app.route("/blockchain")
def blockchain_page():

    return send_from_directory(
        FRONTEND_FOLDER,
        "blockchain.html"
    )


# --------------------------------------------------
# STORAGE PAGE
# --------------------------------------------------

@app.route("/storage")
def storage_page():

    return send_from_directory(
        FRONTEND_FOLDER,
        "storage.html"
    )


# --------------------------------------------------
# CSS
# --------------------------------------------------

@app.route("/style.css")
def styles():

    return send_from_directory(
        FRONTEND_FOLDER,
        "style.css"
    )


# --------------------------------------------------
# JAVASCRIPT FILES
# --------------------------------------------------

@app.route("/script.js")
def scripts():

    return send_from_directory(
        FRONTEND_FOLDER,
        "script.js"
    )


@app.route("/register.js")
def register_scripts():

    return send_from_directory(
        FRONTEND_FOLDER,
        "register.js"
    )


@app.route("/verify.js")
def verify_scripts():

    return send_from_directory(
        FRONTEND_FOLDER,
        "verify.js"
    )


@app.route("/frontend/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# --------------------------------------------------
# BACKEND HEALTH
# --------------------------------------------------

@app.route("/api/health")
def health():

    return jsonify({
        "status": "success",
        "message": "MediTrace backend is running!"
    })


# --------------------------------------------------
# BLOCKCHAIN NETWORK STATUS API
# --------------------------------------------------

@app.route("/api/blockchain/status", methods=["GET"])
def blockchain_network_status():

    try:

        web3, contract = get_blockchain_contract()

        chain_id = web3.eth.chain_id
        latest_block = web3.eth.block_number
        contract_address = contract.address

        contract_code = web3.eth.get_code(contract_address)

        if not contract_code:
            raise Exception("Smart contract is not deployed")

        return jsonify({
            "success": True,
            "connected": True,
            "network": "Ganache" if chain_id == 1337 else "Ethereum",
            "chain_id": chain_id,
            "latest_block": latest_block,
            "contract_address": contract_address,
            "contract_deployed": True
        }), 200

    except Exception:

        app.logger.exception("Blockchain status check failed")

        return jsonify({
            "success": False,
            "connected": False,
            "network": "Unavailable",
            "message": "Blockchain connection failed"
        }), 503


# --------------------------------------------------
# BLOCKCHAIN TRANSACTION RECORDS API
# --------------------------------------------------

@app.route("/api/blockchain/records", methods=["GET"])
def blockchain_records():

    connection = None

    try:

        connection = get_connection()

        rows = connection.execute("""
            SELECT
                medicine_id,
                name,
                batch_id,
                transaction_hash,
                block_number,
                created_at
            FROM medicines
            WHERE transaction_hash IS NOT NULL
              AND block_number IS NOT NULL
            ORDER BY id DESC
        """).fetchall()

        records = []

        for row in rows:

            records.append({
                "medicine_id": row["medicine_id"],
                "name": row["name"],
                "batch_id": row["batch_id"],
                "transaction_hash": row["transaction_hash"],
                "block_number": row["block_number"],
                "created_at": row["created_at"],
                "status": "Recorded"
            })

        return jsonify({
            "success": True,
            "total_records": len(records),
            "records": records
        }), 200

    except Exception:

        app.logger.exception(
            "Blockchain records retrieval failed"
        )

        return jsonify({
            "success": False,
            "message": "Unable to retrieve blockchain records"
        }), 500

    finally:

        if connection is not None:
            connection.close()


# --------------------------------------------------
# DASHBOARD API
# --------------------------------------------------

@app.route("/api/dashboard")
def dashboard():

    connection = sqlite3.connect(
        BASE_FOLDER / "database" / "meditrace.db"
    )

    cursor = connection.cursor()

    total = cursor.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]

    recent = cursor.execute("""
        SELECT name, batch_id, manufacturer
        FROM medicines
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    medicines = []

    for medicine in recent:

        medicines.append({
            "name": medicine[0],
            "batch": medicine[1],
            "manufacturer": medicine[2],
            "status": "Registered"
        })

    try:

        get_blockchain_contract()
        blockchain_status = "Connected"

    except Exception:

        app.logger.exception(
            "Blockchain connection check failed"
        )

        blockchain_status = "Disconnected"

    return jsonify({

        "total_medicines": total,

        "verified_batches": 0,

        "suspicious_batches": 0,

        "storage_alerts": 0,

        "blockchain_status": blockchain_status,

        "medicines": medicines,

        "storage": {
            "temperature": 25,
            "humidity": 55,
            "condition": "Simulated"
        }

    })


# --------------------------------------------------
# REGISTER MEDICINE
# SHA-256 + RSA + ETHEREUM + SQLITE
# --------------------------------------------------

@app.route("/api/medicines", methods=["POST"])
def register_medicine():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Invalid request data"
        }), 400

    required_fields = [
        "name",
        "batch_id",
        "manufacturer",
        "manufacturing_date",
        "expiry_date",
        "quantity"
    ]

    for field in required_fields:

        if field not in data or str(data[field]).strip() == "":

            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    name = str(data["name"]).strip()
    batch_id = str(data["batch_id"]).strip()
    manufacturer = str(data["manufacturer"]).strip()

    if not all([name, batch_id, manufacturer]):

        return jsonify({
            "status": "error",
            "message": "Text fields cannot be empty"
        }), 400

    try:

        # STEP 1: VALIDATE DATES

        manufacturing_date = date.fromisoformat(
            data["manufacturing_date"]
        )

        expiry_date = date.fromisoformat(
            data["expiry_date"]
        )

        if expiry_date <= manufacturing_date:
            raise ValueError(
                "Expiry date must be after manufacturing date"
            )

        if manufacturing_date > date.today():
            raise ValueError(
                "Manufacturing date cannot be in the future"
            )

        # STEP 2: VALIDATE QUANTITY

        quantity = int(data["quantity"])

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        # STEP 3: GENERATE MEDICINE ID

        medicine_id = f"MED-{batch_id}"

        if get_medicine(medicine_id) is not None:

            return jsonify({
                "status": "error",
                "message": "This medicine is already registered"
            }), 409

        # STEP 4: PREPARE MEDICINE INFORMATION

        medicine = {
            "medicine_id": medicine_id,
            "name": name,
            "batch_id": batch_id,
            "manufacturer": manufacturer,
            "manufacturing_date": manufacturing_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "quantity": quantity
        }

        # STEP 5: GENERATE SHA-256 HASH

        medicine_hash = generate_hash(medicine)

        # STEP 6: CREATE RSA DIGITAL SIGNATURE

        digital_signature = create_signature(
            medicine_hash,
            private_key
        )

        # STEP 7: REGISTER HASH ON ETHEREUM

        try:

            blockchain_result = register_on_blockchain(
                medicine_id,
                medicine_hash
            )

        except Exception as error:

            app.logger.exception(
                "Blockchain registration failed"
            )

            return jsonify({
                "status": "error",
                "message": (
                    "Blockchain registration failed: " + str(error)
                )
            }), 503

        # STEP 8: SAVE IN SQLITE

        add_medicine(
            medicine_id,
            name,
            batch_id,
            manufacturer,
            manufacturing_date.isoformat(),
            expiry_date.isoformat(),
            quantity,
            medicine_hash,
            digital_signature,
            blockchain_result["transaction_hash"],
            blockchain_result["block_number"]
        )

        # STEP 9: RETURN SUCCESS RESPONSE

        return jsonify({

            "status": "success",

            "message": (
                "Medicine registered successfully "
                "in SQLite and Ethereum!"
            ),

            "medicine_id": medicine_id,

            "medicine_hash": medicine_hash,

            "digital_signature": digital_signature,

            "blockchain": {

                "status": "success",

                "transaction_hash": (
                    blockchain_result["transaction_hash"]
                ),

                "contract_address": (
                    blockchain_result["contract_address"]
                ),

                "block_number": (
                    blockchain_result["block_number"]
                )

            }

        }), 201

    except sqlite3.IntegrityError:

        return jsonify({
            "status": "error",
            "message": "This batch ID is already registered"
        }), 409

    except (ValueError, TypeError) as error:

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except sqlite3.Error:

        app.logger.exception(
            "Database registration error"
        )

        return jsonify({
            "status": "error",
            "message": "Database error occurred"
        }), 500

    except Exception as error:

        app.logger.exception(
            "Medicine registration failed"
        )

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


# --------------------------------------------------
# DISPLAY QR CODE
# --------------------------------------------------

@app.route("/api/qr/<filename>", methods=["GET"])
def get_qr_code(filename):

    if not filename.endswith(".png"):

        return jsonify({
            "status": "error",
            "message": "Invalid QR code filename"
        }), 400

    return send_from_directory(
        QR_FOLDER,
        filename,
        mimetype="image/png"
    )


# --------------------------------------------------
# MOBILE MEDICINE DETAILS PAGE
# Opens when someone scans the QR code
# --------------------------------------------------

@app.route("/medicine/<medicine_id>", methods=["GET"])
def medicine_details_page(medicine_id):

    record = get_medicine(medicine_id)

    if record is None:

        return "Medicine record not found", 404

    quantity = int(record["quantity"] or 0)

    availability = get_medicine_availability(
        quantity,
        record["expiry_date"]
    )

    try:

        manufacturing_date = date.fromisoformat(
            record["manufacturing_date"]
        ).strftime("%d %B %Y")

    except (ValueError, TypeError):

        manufacturing_date = "Not recorded"

    try:

        expiry_date = date.fromisoformat(
            record["expiry_date"]
        ).strftime("%d %B %Y")

    except (ValueError, TypeError):

        expiry_date = "Not recorded"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>MediTrace - Medicine Details</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                margin: 0;
                padding: 20px;
                color: #1e293b;
            }

            .container {
                max-width: 550px;
                margin: 30px auto;
                background: white;
                padding: 25px;
                border-radius: 14px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }

            h1 {
                text-align: center;
                color: #0f766e;
            }

            .subtitle {
                text-align: center;
                color: #64748b;
                margin-bottom: 25px;
            }

            .verified {
                background: #dcfce7;
                color: #166534;
                padding: 12px;
                text-align: center;
                border-radius: 8px;
                margin-bottom: 20px;
                font-weight: bold;
            }

            .detail {
                padding: 13px 0;
                border-bottom: 1px solid #e2e8f0;
            }

            .detail strong {
                display: block;
                color: #475569;
                margin-bottom: 5px;
            }

            .detail span {
                font-size: 16px;
                overflow-wrap: anywhere;
            }

            .footer {
                text-align: center;
                color: #64748b;
                font-size: 13px;
                margin-top: 25px;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>MediTrace</h1>

            <p class="subtitle">
                Medicine Authenticity and Storage Tracker
            </p>

            <div class="verified">
                ✓ Medicine details retrieved from MediTrace
            </div>

            <div class="detail">
                <strong>Medicine Name</strong>
                <span>{{ name }}</span>
            </div>

            <div class="detail">
                <strong>Medicine ID</strong>
                <span>{{ medicine_id }}</span>
            </div>

            <div class="detail">
                <strong>Batch ID</strong>
                <span>{{ batch_id }}</span>
            </div>

            <div class="detail">
                <strong>Manufacturer</strong>
                <span>{{ manufacturer }}</span>
            </div>

            <div class="detail">
                <strong>Manufacturing Date</strong>
                <span>{{ manufacturing_date }}</span>
            </div>

            <div class="detail">
                <strong>Expiry Date</strong>
                <span>{{ expiry_date }}</span>
            </div>

            <div class="detail">
                <strong>Available Quantity</strong>
                <span>{{ quantity }}</span>
            </div>

            <div class="detail">
                <strong>Availability</strong>
                <span>{{ availability }}</span>
            </div>

            <div class="footer">
                MediTrace Academic Project
            </div>

        </div>

    </body>
    </html>
    """,

    name=record["name"],
    medicine_id=record["medicine_id"],
    batch_id=record["batch_id"],
    manufacturer=record["manufacturer"],
    manufacturing_date=manufacturing_date,
    expiry_date=expiry_date,
    quantity=quantity,
    availability=availability
    )


# --------------------------------------------------
# VERIFY MEDICINE
# SHA-256 + RSA + ETHEREUM + QR GENERATION
# --------------------------------------------------

@app.route("/api/verify", methods=["POST"])
def verify_medicine():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "Invalid request data"
        }), 400

    medicine_id = str(
        data.get("medicine_id", "")
    ).strip()

    if not medicine_id:

        return jsonify({
            "status": "error",
            "message": "Medicine ID is required"
        }), 400

    # STEP 1: GET MEDICINE FROM DATABASE

    record = get_medicine(medicine_id)

    if record is None:

        return jsonify({
            "status": "error",
            "authentic": False,
            "message": "Medicine record not found"
        }), 404

    if not record["medicine_hash"] or not record["digital_signature"]:

        return jsonify({
            "status": "error",
            "authentic": False,
            "message": "This record has no cryptographic signature."
        }), 400

    # STEP 2: VERIFY SHA-256

    current_payload = medicine_payload(record)

    current_hash = generate_hash(current_payload)

    hash_matches = hmac.compare_digest(
        current_hash,
        record["medicine_hash"]
    )

    # STEP 3: VERIFY RSA DIGITAL SIGNATURE

    signature_valid = verify_signature(
        record["medicine_hash"],
        record["digital_signature"],
        public_key
    )

    # STEP 4: VERIFY ETHEREUM

    try:

        blockchain_result = verify_on_blockchain(
            medicine_id,
            record["medicine_hash"]
        )

    except Exception as error:

        app.logger.exception(
            "Blockchain verification failed"
        )

        return jsonify({
            "status": "error",
            "authentic": False,
            "message": (
                "Blockchain verification unavailable: " + str(error)
            )
        }), 503

    blockchain_verified = (
        blockchain_result["exists"]
        and blockchain_result["hash_matches"]
    )

    # STEP 5: FINAL VERIFICATION

    authentic = (
        hash_matches
        and signature_valid
        and blockchain_verified
    )

    qr_filename = None
    qr_code_url = None
    medicine_details = None

    # STEP 6: GENERATE QR ONLY IF MEDICINE IS AUTHENTIC

    if authentic:

        quantity = int(record["quantity"] or 0)

        manufacturing_date_raw = record["manufacturing_date"]
        expiry_date_raw = record["expiry_date"]

        try:

            manufacturing_date = date.fromisoformat(
                manufacturing_date_raw
            ).strftime("%d %B %Y")

        except (ValueError, TypeError):

            manufacturing_date = "Not recorded"

        try:

            expiry_date = date.fromisoformat(
                expiry_date_raw
            ).strftime("%d %B %Y")

        except (ValueError, TypeError):

            expiry_date = "Not recorded"

        availability = get_medicine_availability(
            quantity,
            expiry_date_raw
        )

        medicine_details = {

            "medicine_name": record["name"],

            "medicine_id": record["medicine_id"],

            "batch_id": record["batch_id"],

            "manufacturer": record["manufacturer"],

            "manufacturing_date": manufacturing_date,

            "expiry_date": expiry_date,

            "available_quantity": quantity,

            "availability": availability

        }

        # QR CONTAINS A WEBPAGE URL
        # The phone opens this page after scanning.

        medicine_url = (
            "http://192.168.222.2:5000"
            + f"/medicine/{medicine_id}"
        )

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )

        qr.add_data(medicine_url)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        qr_filename = f"{medicine_id}.png"

        qr_path = QR_FOLDER / qr_filename

        qr_image.save(qr_path)

        qr_code_url = f"/api/qr/{qr_filename}"

    # STEP 7: RETURN VERIFICATION RESULT

    return jsonify({

        "status": "success",

        "medicine_id": medicine_id,

        "authentic": authentic,

        "hash_matches": hash_matches,

        "signature_valid": signature_valid,

        "blockchain_verified": blockchain_verified,

        "blockchain_record_exists": blockchain_result["exists"],

        "stored_hash": record["medicine_hash"],

        "current_hash": current_hash,

        "message": (
            "Medicine verified successfully! SHA-256, RSA and Ethereum checks passed."
            if authentic
            else "WARNING: Medicine authenticity verification failed!"
        ),

        "medicine_details": medicine_details,

        "qr_code": qr_filename,

        "qr_code_url": qr_code_url

    }), 200


# --------------------------------------------------
# STORAGE DASHBOARD API
# --------------------------------------------------

@app.route("/api/storage", methods=["GET"])
def storage_dashboard():

    connection = None

    try:

        connection = get_connection()

        rows = connection.execute("""
            SELECT
                medicine_id,
                name,
                batch_id,
                quantity,
                expiry_date
            FROM medicines
            ORDER BY expiry_date ASC
        """).fetchall()

        today = date.today()

        expiry_warning_date = today + timedelta(days=30)

        expiring_soon_count = 0
        medicines = []
        total_stock = 0
        expired_count = 0
        available_count = 0
        low_stock_count = 0

        LOW_STOCK_LIMIT = 50

        for row in rows:

            medicine = dict(row)

            quantity = int(medicine["quantity"] or 0)

            try:

                expiry = date.fromisoformat(
                    medicine["expiry_date"]
                )

            except (ValueError, TypeError):

                expiry = None

            if expiry is not None and expiry < today:

                status = "Expired"
                expired_count += 1

            elif quantity <= 0:

                status = "Out of Stock"

            elif expiry is not None and expiry <= expiry_warning_date:

                status = "Expiring Soon"
                expiring_soon_count += 1
                available_count += 1

            elif quantity <= LOW_STOCK_LIMIT:

                status = "Low Stock"
                low_stock_count += 1
                available_count += 1

            else:

                status = "Available"
                available_count += 1

            total_stock += quantity

            medicine["status"] = status

            medicines.append(medicine)

        return jsonify({

            "success": True,

            "expiring_soon_medicines": expiring_soon_count,

            "total_medicines": len(medicines),

            "total_stock": total_stock,

            "available_medicines": available_count,

            "expired_medicines": expired_count,

            "low_stock_medicines": low_stock_count,

            "medicines": medicines

        }), 200

    except Exception as error:

        app.logger.exception(
            "Storage dashboard error"
        )

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        debug=True,
        port=5000,
        use_reloader=False
    )