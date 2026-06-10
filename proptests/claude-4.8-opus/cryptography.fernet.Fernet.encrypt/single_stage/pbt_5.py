from hypothesis import given, strategies as st

# Summary: Generate arbitrary byte strings (including empty, null bytes,
# high-value bytes, and large payloads) via st.binary(). For each, create a
# fresh Fernet key, encrypt the data, and verify the token is bytes, is valid
# URL-safe base64, and decrypts back to the exact original data.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    import base64
    from cryptography.fernet import Fernet

    drawn_data = data.draw(st.binary(min_size=0, max_size=4096))

    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(drawn_data)

    # Property 1: encrypt returns bytes
    assert isinstance(token, bytes)

    # Property 2: token is non-empty
    assert len(token) > 0

    # Property 3: token is valid URL-safe base64
    decoded = base64.urlsafe_b64decode(token)
    assert isinstance(decoded, bytes)

    # Property 4: round-trip decryption returns the exact original data
    assert f.decrypt(token) == drawn_data
# End program