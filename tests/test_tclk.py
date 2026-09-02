from technocore.tclk import generate_secret_preimage, verify_lock, LockOffer, parse_offer_frame

def test_tclk_primitives():
    secret, lock = generate_secret_preimage()
    assert verify_lock(secret, lock) is True
    assert verify_lock("00" * 32, lock) is False

def test_lock_offer_frame():
    offer = LockOffer(
        offer_id="off_123",
        room="lobby",
        sender_did="did:key:z6MkpBJVDkWTk8eUttpcWnUTKVeyHk6458tvvtwKfaKRabht",
        receiver_did="did:key:z6MktEBkPiEi...",
        hash_lock="a"*64,
        deadline_ts=1750000000,
        amount="100.0",
        rail="flop-escrow"
    )
    frame = offer.to_frame()
    assert "[tclk/1:offer]" in frame
    parsed = parse_offer_frame(frame)
    assert parsed is not None
    assert parsed["id"] == "off_123"
    assert parsed["amount"] == "100.0"
