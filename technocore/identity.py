"""Encrypted Ed25519 identity (agent DID) management."""
import base64
import time
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption

from .keys import did_from_pubkey, pubkey_raw_from_did

MIN_PASSPHRASE = 12


def _priv_to_pem(key: Ed25519PrivateKey, passphrase: str) -> bytes:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        BestAvailableEncryption(passphrase.encode()),
    )


@dataclass
class Identity:
    signing_key: Ed25519PrivateKey

    @property
    def did(self) -> str:
        raw = self.signing_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        return did_from_pubkey(raw)

    def sign(self, payload: bytes) -> str:
        """Unpadded base64url Ed25519 signature."""
        return (
            base64.urlsafe_b64encode(self.signing_key.sign(payload))
            .decode("ascii")
            .rstrip("=")
        )

    def save(self, path: str | Path, passphrase: str) -> Path:
        if len(passphrase) < MIN_PASSPHRASE:
            raise ValueError(f"passphrase needs {MIN_PASSPHRASE}+ characters")
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(_priv_to_pem(self.signing_key, passphrase))
        p.chmod(0o600)
        return p

    @classmethod
    def generate(cls) -> "Identity":
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def load(cls, path: str | Path, passphrase: str) -> "Identity":
        pem = Path(path).expanduser().read_bytes()
        try:
            key = serialization.load_pem_private_key(
                pem, password=passphrase.encode()
            )
        except Exception as e:  # wrong passphrase or corrupt file
            raise ValueError(f"cannot load identity: {e}") from e
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("identity file does not hold an Ed25519 private key")
        return cls(key)


def verify(did: str, signature: str, payload: bytes) -> bool:
    """Check an unpadded-base64url signature against a did:key."""
    pad = "=" * (-len(signature) % 4)
    raw_sig = base64.urlsafe_b64decode(signature + pad)
    pub = Ed25519PublicKey.from_public_bytes(pubkey_raw_from_did(did))
    try:
        pub.verify(raw_sig, payload)
        return True
    except Exception:
        return False


def next_nonce() -> str:
    """Wall-clock nonce, 1-19 digits, per the signed-write protocol."""
    return str(time.time_ns())
