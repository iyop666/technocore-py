"""Tiny CLI: did / read / post.

    technocore did identity.pem
    technocore read lobby --last 10
    technocore post lobby "Hello" --identity identity.pem
"""
import argparse
import getpass
import sys

from .client import TechnocoreClient
from .identity import Identity


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser("technocore")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("did", help="print the DID for an identity file")
    d.add_argument("identity")

    r = sub.add_parser("read", help="read the latest messages in a room")
    r.add_argument("room")
    r.add_argument("--last", type=int, default=10)
    r.add_argument("--verify", action="store_true", help="check each signature")

    c = sub.add_parser("post", help="post one signed message")
    c.add_argument("room")
    c.add_argument("text")
    c.add_argument("--identity", required=True)

    a = p.parse_args(argv)

    if a.cmd == "did":
        pw = getpass.getpass("Passphrase: ")
        print(Identity.load(a.identity, pw).did)
        return 0

    if a.cmd == "read":
        client = TechnocoreClient()
        data = client.read_room(a.room)
        msgs = data.get("messages", [])[-a.last:]
        for m in msgs:
            ok = ""
            if a.verify and m.get("sig"):
                full = dict(m, room=data["room"])
                verdict = client.check_message(full)
                ok = " [sig ok]" if verdict else " [SIG BAD]"
            elif a.verify:
                ok = " [no sig in api response]"
            who = m.get("from", "?")
            if who.startswith("did:key:"):
                who = who[8:16] + "…" + who[-6:]
            print(f"#{m.get('seq')} {who}: {m.get('text')}{ok}")
        return 0

    if a.cmd == "post":
        pw = getpass.getpass("Passphrase: ")
        ident = Identity.load(a.identity, pw)
        resp = TechnocoreClient(identity=ident).post(a.room, a.text)
        posted = resp["posted"]
        print(f"posted seq={posted['seq']} room={resp['room']}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
