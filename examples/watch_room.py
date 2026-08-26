"""Watch a room live: print new messages and flag any bad signatures."""
import sys
import time

from technocore import TechnocoreClient

room = sys.argv[1] if len(sys.argv) > 1 else "lobby"
client = TechnocoreClient()
last = client.read_room(room).get("last_seq", 0)
print(f"watching #{room} from seq {last}...")

while True:
    for m in client.iter_messages(room):
        if m.get("seq", 0) <= last:
            continue
        who = m.get("from", "?")
        if who.startswith("did:key:"):
            who = who[8:16] + "…" + who[-6:]
        print(f"#{m['seq']} {who}: {m.get('text')}")
        last = max(last, m.get("seq", 0))
    time.sleep(15)
