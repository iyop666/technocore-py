"""Technocore Lock Protocol (tclk/1) primitive helpers for python."""
import hashlib
import os
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Any, Tuple


def generate_secret_preimage(bytes_count: int = 32) -> Tuple[str, str]:
    """Generate secret s (hex) and its SHA-256 hash lock (hex)."""
    raw = secrets.token_bytes(bytes_count)
    secret_hex = raw.hex()
    lock_hex = hashlib.sha256(raw).hexdigest()
    return secret_hex, lock_hex


def verify_lock(secret_hex: str, lock_hex: str) -> bool:
    """Verify that sha256(secret_hex) == lock_hex."""
    try:
        raw = bytes.fromhex(secret_hex)
        return hashlib.sha256(raw).hexdigest().lower() == lock_hex.lower()
    except Exception:
        return False


@dataclass
class LockOffer:
    offer_id: str
    room: str
    sender_did: str
    receiver_did: str
    hash_lock: str
    deadline_ts: int
    amount: str
    rail: str = "flop-escrow"

    def to_frame(self) -> str:
        return (
            f"[tclk/1:offer] id={self.offer_id} to={self.receiver_did} "
            f"lock={self.hash_lock} deadline={self.deadline_ts} "
            f"amount={self.amount} rail={self.rail}"
        )


def parse_offer_frame(text: str) -> Dict[str, str] | None:
    if not text.startswith("[tclk/1:offer]"):
        return None
    parts = text.split()[1:]
    res = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            res[k] = v
    return res
