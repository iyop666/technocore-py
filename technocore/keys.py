"""Low-level encoding helpers for did:key (Ed25519, base58btc multibase)."""
import re

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_INDEX = {c: i for i, c in enumerate(BASE58_ALPHABET)}
ED25519_PREFIX = b"\xed\x01"
DID_RE = re.compile(r"^did:key:(z[1-9A-HJ-NP-Za-km-z]{47})$")


def b58_encode(data: bytes) -> str:
    zeroes = len(data) - len(data.lstrip(b"\x00"))
    n = int.from_bytes(data, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = BASE58_ALPHABET[r] + out
    return "1" * zeroes + out


def b58_decode(text: str) -> bytes:
    n = 0
    for ch in text:
        if ch not in _BASE58_INDEX:
            raise ValueError(f"invalid base58 character: {ch!r}")
        n = n * 58 + _BASE58_INDEX[ch]
    body = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * (len(text) - len(text.lstrip("1"))) + body


def did_from_pubkey(raw: bytes) -> str:
    """raw = 32-byte Ed25519 public key. Returns did:key:z6Mk..."""
    return "did:key:z" + b58_encode(ED25519_PREFIX + raw)


def pubkey_raw_from_did(did: str) -> bytes:
    m = DID_RE.match(did or "")
    if not m:
        raise ValueError("expected canonical did:key:z6Mk... (48-char multibase)")
    decoded = b58_decode(m.group(1)[1:])
    if not decoded.startswith(ED25519_PREFIX) or len(decoded) != 34:
        raise ValueError("multibase does not wrap an ed25519-pub key")
    return decoded[2:]
