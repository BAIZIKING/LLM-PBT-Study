from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Summary: Generate arbitrary byte strings (including empty, small, large, and
# arbitrary byte values) using st.binary(). For each, encrypt with a fresh Fernet
# key and verify: (1) the result is bytes, (2) it is valid URL-safe base64,
# and (3) decrypting the token recovers the original data exactly (round-trip).
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    payload = data.draw(st.binary(min_size=0, max_size=4096))

    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(payload)

    # Property 1: encrypt returns bytes
    assert isinstance(token, bytes)

    # Property 2: token is URL-safe base64-encoded (only valid alphabet chars)
    urlsafe_b64_alphabet = set(
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        b"abcdefghijklmnopqrstuvwxyz"
        b"0123456789-_="
    )
    assert all(byte in urlsafe_b64_alphabet for byte in token)

    # Property 3: round-trip decryption recovers the original data exactly
    assert f.decrypt(token) == payload
# End program