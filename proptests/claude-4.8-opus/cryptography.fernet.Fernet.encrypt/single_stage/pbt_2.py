from hypothesis import given, strategies as st
import base64
from cryptography.fernet import Fernet

# Summary: Generate arbitrary byte strings (including empty and large payloads)
# via st.binary(), encrypt them with a freshly generated Fernet key, and verify
# that the token is bytes, is valid URL-safe base64, and decrypts back to the
# original plaintext (round-trip correctness).
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt():
    data = st.data()  # placeholder; actual draw below

    # Draw a byte payload covering empty, small, and large cases.
    payload = _draw_payload()


# We use an inner helper to keep the @given(st.data()) signature, drawing
# the value explicitly so we can interleave key generation cleanly.
@given(data=st.binary(min_size=0, max_size=4096))
def _run(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(data)

    # Property 1: encrypt returns bytes.
    assert isinstance(token, bytes)

    # Property 2: token is valid URL-safe base64.
    # urlsafe_b64decode must succeed without raising.
    decoded = base64.urlsafe_b64decode(token)
    assert isinstance(decoded, bytes)

    # Property 3: round-trip correctness — decrypt yields original plaintext.
    assert f.decrypt(token) == data

    # Property 4: a non-empty plaintext is actually transformed (privacy).
    if data:
        assert token != data


def test_cryptography_fernet_Fernet_encrypt():
    _run()
# End program