"""Stateless signature verifier for Technocore contribution proofs."""
import json
import sys
from pathlib import Path

from technocore.identity import verify
from technocore.keys import pubkey_raw_from_did


def _contribution_payload(artifact_url: str, commit: str) -> bytes:
    record = {
        "artifact_url": artifact_url,
        "commit": commit.lower(),
        "schema": "technocore-contribution-v1",
    }
    canonical = json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return canonical.encode("utf-8")


def verify_proof_file(path: str | Path) -> dict:
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"proof file not found: {path}")
    
    data = json.loads(p.read_text())
    schema = data.get("schema")
    if schema != "technocore-contribution-proof-v1":
        raise ValueError(f"unsupported schema: {schema}")

    did = data.get("did", "")
    sig = data.get("signature", "")
    artifact_url = data.get("artifact_url", "")
    commit = data.get("commit", "")

    if not did or not sig or not artifact_url or not commit:
        raise ValueError("missing required proof fields (did, signature, artifact_url, commit)")

    # Validate DID format
    pubkey_raw_from_did(did)

    payload = _contribution_payload(artifact_url, commit)
    is_valid = verify(did, sig, payload)
    return {
        "valid": is_valid,
        "did": did,
        "artifact_url": artifact_url,
        "commit": commit,
        "schema": schema,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: technocore-verify-proof <path-to-proof.json>")
        sys.exit(1)

    proof_path = sys.argv[1]
    try:
        res = verify_proof_file(proof_path)
        if res["valid"]:
            print(f"✅ VALID PROOF")
            print(f"  DID:      {res['did']}")
            print(f"  Artifact: {res['artifact_url']}")
            print(f"  Commit:   {res['commit']}")
            sys.exit(0)
        else:
            print(f"❌ INVALID PROOF SIGNATURE")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️ Error verifying proof: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
