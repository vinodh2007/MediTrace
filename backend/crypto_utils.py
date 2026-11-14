
import hashlib
import json
import base64

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


# Key storage location
BASE_DIR = Path(__file__).resolve().parent

KEY_DIR = BASE_DIR / "keys"

PRIVATE_KEY_PATH = KEY_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public_key.pem"


# Generate RSA keys if they do not exist


def load_or_create_keys():

    KEY_DIR.mkdir(parents=True, exist_ok=True)

    # Generate new keys if either key is missing
    if not PRIVATE_KEY_PATH.exists() or not PUBLIC_KEY_PATH.exists():

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        public_key = private_key.public_key()

        # Save private key
        with open(PRIVATE_KEY_PATH, "wb") as file:

            file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save public key
        with open(PUBLIC_KEY_PATH, "wb") as file:

            file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

        return private_key, public_key

    # Load existing valid keys
    try:

        with open(PRIVATE_KEY_PATH, "rb") as file:

            private_key = serialization.load_pem_private_key(
                file.read(),
                password=None
            )

        with open(PUBLIC_KEY_PATH, "rb") as file:

            public_key = serialization.load_pem_public_key(
                file.read()
            )

        return private_key, public_key

    except (ValueError, TypeError):

        raise RuntimeError(
            "RSA key files are corrupted. "
            "Delete both PEM files and restart the application."
        )
 


# Convert medicine details into consistent bytes
def canonical_medicine_data(medicine):

    medicine_json = json.dumps(
        medicine,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return medicine_json.encode("utf-8")


# Generate SHA-256 hash
def generate_hash(medicine):

    medicine_bytes = canonical_medicine_data(medicine)

    return hashlib.sha256(medicine_bytes).hexdigest()


# Create RSA digital signature
def create_signature(hash_value, private_key):

    signature = private_key.sign(

        hash_value.encode("utf-8"),

        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),

        hashes.SHA256()
    )

    return base64.b64encode(signature).decode("utf-8")


# Verify RSA digital signature
def verify_signature(hash_value, signature_text, public_key):

    try:

        signature = base64.b64decode(
            signature_text,
            validate=True
        )

        public_key.verify(

            signature,

            hash_value.encode("utf-8"),

            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),

            hashes.SHA256()
        )

        return True

    except (InvalidSignature, ValueError, TypeError):
        return False
