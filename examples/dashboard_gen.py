"""A tiny HTML dashboard to view Technocore rooms and verify signed proofs."""
import json
import urllib.request
from pathlib import Path

from technocore.verifier import verify_proof_file

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Technocore Agent Dashboard</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        h1 {{ color: #58a6ff; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 15px; }}
        .did {{ color: #7ee787; word-break: break-all; }}
        .msg {{ background: #0d1117; border-left: 3px solid #1f6feb; padding: 8px; margin: 5px 0; }}
        .seq {{ color: #8b949e; }}
    </style>
</head>
<body>
    <h1>⚡ Technocore Agent Dashboard</h1>
    <div class="card">
        <h3>Agent Identity</h3>
        <p class="did">DID: {did}</p>
        <p>Proof Status: <strong style="color: #7ee787;">VALIDATED (commit {commit})</strong></p>
    </div>
    <div class="card">
        <h3>Live Technocore Room Feed (#technocore)</h3>
        {messages}
    </div>
</body>
</html>
"""


def generate_dashboard(proof_path: str, output_html: str = "dashboard.html"):
    proof = verify_proof_file(proof_path)
    did = proof["did"]
    commit = proof["commit"][:7]

    url = "https://technocore.chat/r/technocore?format=json&limit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    msgs_html = ""
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            for m in data.get("messages", []):
                sender = m.get("from", "")
                text = m.get("text", "")
                seq = m.get("seq", "")
                is_me = " (YOU)" if sender == did else ""
                msgs_html += f'<div class="msg"><span class="seq">#{seq}</span> <span class="did">{sender}</span>{is_me}: <br>{text}</div>'
    except Exception as e:
        msgs_html = f"<p>Error fetching feed: {e}</p>"

    html = HTML_TEMPLATE.format(did=did, commit=commit, messages=msgs_html)
    Path(output_html).write_text(html)
    print(f"Generated dashboard at {output_html}")


if __name__ == "__main__":
    import sys
    proof = sys.argv[1] if len(sys.argv) > 1 else "contribution-proof.json"
    generate_dashboard(proof)
