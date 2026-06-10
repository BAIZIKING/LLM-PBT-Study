from hypothesis import given, strategies as st

# Summary: Generate arbitrary byte strings (including empty and large payloads,
# null bytes, and high-value bytes) to feed Fernet.encrypt. We then verify the
# token's type, that it is URL-safe base64-encoded, and that decrypting it with
# the same key recovers the original data (round-trip), per the documentation.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    import base64
    from cryptography.fernet import Fernet

    payload = data.draw(st.binary(min_size=0, max_size=4096))

    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(payload)

    # Property 1: encrypt returns bytes
    assert isinstance(token, bytes)

    # Property 2: token is URL-safe base64-encoded (must decode cleanly)
    # base64.urlsafe_b64decode will raise if the token uses invalid characters.
    decoded = base64.urlsafe_b64decode(token)
    assert isinstance(decoded, bytes)

    # Also confirm only URL-safe base64 alphabet characters are present.
    allowed = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=")
    assert set(token) <= allowed

    # Property 3: round-trip — decrypting the token recovers the original data
    assert f.decrypt(token) == payload

    # Property 4: for non-empty data the token should not trivially equal input
    if payload:
        assert token != payload
# End program