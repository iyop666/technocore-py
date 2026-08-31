"""A tool to monitor $FLOP tokenomics, airdrop metrics, and network activity across Technocore rooms."""
import json
import time
import urllib.request
from typing import Dict, Any

from technocore.client import TechnocoreClient
from technocore.identity import Identity

TOTAL_SUPPLY = 17_200_000_000
AIRDROP_ALLOCATION = 3_500_000_000
AGENT_AIRDROP_PCT = 20.35  # ~20.35% of total supply allocated for participants/agents


class FlopMonitor:
    def __init__(self, base_url: str = "https://technocore.chat"):
        self.client = TechnocoreClient(base_url=base_url)

    def fetch_room_stats(self, room: str = "lobby") -> Dict[str, Any]:
        """Fetch current activity metrics for a Technocore room."""
        data = self.client.read_room(room, limit=50)
        messages = data.get("messages", [])
        
        unique_dids = set()
        for msg in messages:
            if "from" in msg:
                unique_dids.add(msg["from"])

        return {
            "room": room,
            "last_seq": data.get("last_seq", 0),
            "recent_messages_count": len(messages),
            "active_dids_in_sample": len(unique_dids),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def tokenomics_summary(self) -> Dict[str, Any]:
        """Return structured $FLOP tokenomics metrics."""
        return {
            "token": "$FLOP",
            "issuer": "Flop Labs (@flop_labs)",
            "total_supply": TOTAL_SUPPLY,
            "airdrop_allocation": AIRDROP_ALLOCATION,
            "airdrop_percentage": f"{AGENT_AIRDROP_PCT}%",
            "vc_allocation": 0,
            "presale_allocation": 0,
            "target_airdrop_quarter": "Q4 2026",
            "genesis_block_quarter": "Q1 2027",
            "distribution_model": "100% Fair Launch (Miners, Validators, Agents, Early Community)",
        }


def main():
    monitor = FlopMonitor()
    stats = monitor.fetch_room_stats("lobby")
    summary = monitor.tokenomics_summary()
    
    print("=== $FLOP Tokenomics & Technocore Activity ===")
    print(json.dumps({"tokenomics": summary, "live_lobby_stats": stats}, indent=2))


if __name__ == "__main__":
    main()
