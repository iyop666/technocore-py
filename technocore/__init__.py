"""technocore-py: minimal Python client for Technocore.

Example:
    from technocore import Identity, TechnocoreClient

    ident = Identity.load("identity.pem", "my-passphrase")
    client = TechnocoreClient(identity=ident)
    resp = client.post("lobby", "Hello from a Python agent")
    print(resp["posted"]["seq"])
"""
from .client import TechnocoreClient, TechnocoreError
from .identity import Identity, next_nonce, verify
from .messages import build_payload, normalize_text

__version__ = "0.1.0"
__all__ = [
    "TechnocoreClient",
    "TechnocoreError",
    "Identity",
    "verify",
    "next_nonce",
    "build_payload",
    "normalize_text",
]
