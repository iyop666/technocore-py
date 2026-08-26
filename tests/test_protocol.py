"""Offline protocol tests: no network needed."""
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from technocore import Identity, build_payload, normalize_text, verify
from technocore.keys import b58_decode, b58_encode, did_from_pubkey, pubkey_raw_from_did


def test_base58_roundtrip():
    data = b"\x00\x00hello world\x01"
    assert b58_decode(b58_encode(data)) == data


def test_did_format():
    key = Ed25519PrivateKey.generate()
    raw = key.public_key().public_bytes_raw()
    did = did_from_pubkey(raw)
    assert did.startswith("did:key:z6Mk")
    assert len(did) == 56  # 8 prefix + z + 48 multibase
    assert pubkey_raw_from_did(did) == raw


def test_normalize_strips_invisible():
    assert normalize_text("  hello\u200bworld\n") == "hello world"


def test_payload_shape():
    text, payload = build_payload("lobby", 1234567890123456789, "hi")
    assert payload == b"lobby|1234567890123456789|hi"
    assert text == "hi"


def test_sign_verify_roundtrip():
    ident = Identity.generate()
    _, payload = build_payload("lobby", "123", "signed hello")
    sig = ident.sign(payload)
    assert verify(ident.did, sig, payload)
    assert not verify(ident.did, sig, b"lobby|123|tampered")


def test_identity_save_load(tmp_path):
    ident = Identity.generate()
    pem = tmp_path / "id.pem"
    ident.save(pem, "a-long-test-passphrase")
    loaded = Identity.load(pem, "a-long-test-passphrase")
    assert loaded.did == ident.did
    with pytest.raises(ValueError):
        Identity.load(pem, "wrong-passphrase-xx")


def test_save_rejects_short_passphrase(tmp_path):
    with pytest.raises(ValueError):
        Identity.generate().save(tmp_path / "x.pem", "short")
