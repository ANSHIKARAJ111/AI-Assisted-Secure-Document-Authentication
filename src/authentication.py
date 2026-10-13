
import hashlib
import json
import base64
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


KEY_DIR = Path("keys")
PRIVATE_KEY_PATH = KEY_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public_key.pem"


def generate_keys():
    """Generate signing keys only if they do not already exist."""
    KEY_DIR.mkdir(exist_ok=True)

    if PRIVATE_KEY_PATH.exists() or PUBLIC_KEY_PATH.exists():
        if not (PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists()):
            raise RuntimeError("Incomplete key pair. Restore the missing key.")
        return

    private_key = Ed25519PrivateKey.generate()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    PRIVATE_KEY_PATH.write_bytes(private_bytes)
    PUBLIC_KEY_PATH.write_bytes(public_bytes)


def calculate_hash(document_bytes):
    """Generate SHA-256 fingerprint."""
    return hashlib.sha256(document_bytes).hexdigest()


def canonical_payload(document_id, document_hash):
    """Create a deterministic byte representation for signing."""
    payload = {
        "document_id": document_id,
        "sha256": document_hash,
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sign_document(document_bytes, document_id):
    """Create a signed authentication record."""
    generate_keys()

    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=None
    )

    document_hash = calculate_hash(document_bytes)
    payload = canonical_payload(document_id, document_hash)
    signature = private_key.sign(payload)

    return {
        "document_id": document_id,
        "sha256": document_hash,
        "signature": base64.b64encode(signature).decode("ascii"),
        "algorithm": "Ed25519",
    }


def verify_document(document_bytes, record):
    """Verify signed record and document integrity."""
    try:
        public_key = serialization.load_pem_public_key(
            PUBLIC_KEY_PATH.read_bytes()
        )

        if record.get("algorithm") != "Ed25519":
            return False, "Unsupported signature algorithm"

        payload = canonical_payload(
            record["document_id"],
            record["sha256"]
        )

        signature = base64.b64decode(
            record["signature"], validate=True
        )

        public_key.verify(signature, payload)

        actual_hash = calculate_hash(document_bytes)

        if actual_hash != record["sha256"]:
            return False, "Document has been modified"

        return True, "Document is authentic and unchanged"

    except InvalidSignature:
        return False, "Invalid digital signature"
    except (KeyError, ValueError, TypeError, OSError):
        return False, "Invalid record or missing verification key"
