from technocore.verifier import verify_proof_file

def test_verify_proof_valid():
    res = verify_proof_file("contribution-proof.json")
    assert res["valid"] is True
    assert res["did"] == "did:key:z6MkpBJVDkWTk8eUttpcWnUTKVeyHk6458tvvtwKfaKRabht"
    assert res["artifact_url"] == "https://github.com/iyop666/technocore-py"
