from technocore.flop_analytics import FlopMonitor, TOTAL_SUPPLY, AIRDROP_ALLOCATION

def test_flop_analytics():
    monitor = FlopMonitor()
    summary = monitor.tokenomics_summary()
    assert summary["token"] == "$FLOP"
    assert summary["total_supply"] == TOTAL_SUPPLY
    assert summary["airdrop_allocation"] == AIRDROP_ALLOCATION
    assert summary["vc_allocation"] == 0
