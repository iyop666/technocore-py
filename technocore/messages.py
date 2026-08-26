"""Message normalization and signed-payload construction (server-compatible)."""
import re
import unicodedata

INVISIBLE = frozenset({"Cc", "Cf", "Cs", "Co", "Zl", "Zp"})
MAX_MESSAGE_CHARS = 4096
ROOM_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
NONCE_RE = re.compile(r"^[0-9]{1,19}$")


def normalize_room(room: str) -> str:
    if not ROOM_RE.match(room or ""):
        raise ValueError("room must match ^[a-z0-9][a-z0-9_-]{0,47}$")
    return room


def normalize_text(text: str) -> str:
    """Mirror the server's single-line sweep: invisible chars -> space, strip."""
    cleaned = "".join(
        " " if unicodedata.category(c) in INVISIBLE else c for c in text
    ).strip()
    if not cleaned:
        raise ValueError("message has no visible text after normalization")
    if len(cleaned) > MAX_MESSAGE_CHARS:
        raise ValueError(f"message exceeds {MAX_MESSAGE_CHARS} characters")
    return cleaned


def build_payload(room: str, nonce: str | int, text: str) -> tuple[str, bytes]:
    """Returns (normalized_text, signed_payload_bytes) where
    payload = b"{room}|{nonce}|{normalized_text}".
    """
    nonce_s = str(nonce)
    if not NONCE_RE.match(nonce_s):
        raise ValueError("nonce must be 1-19 ASCII digits")
    normalized = normalize_text(text)
    return normalized, f"{normalize_room(room)}|{nonce_s}|{normalized}".encode()
