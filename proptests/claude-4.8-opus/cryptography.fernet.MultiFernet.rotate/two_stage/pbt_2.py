from hypothesis import given, strategies as st
import base64
import struct
from cryptography.fernet import Fernet, MultiFernet


def _extract_timestamp(token_bytes):
    # Fernet token: version(1) | timestamp(8) | IV(16) | ct | HMAC(32)
    raw = base64.urlsafe_b64decode(token_bytes)
    return struct.unpack(">Q", raw[1:9])[0]


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property(data):
    # Draw a plaintext message (bounded to avoid huge inputs / overflow concerns)
    msg = data.draw(st.binary(min_size=0, max_size=1024))

    # Draw the number of keys for the original MultiFernet instance.
    n_keys = data.draw(st.integers(min_value=1, max_value=4))
    keys = [Fernet(Fernet.generate_key()) for _ in range(n_keys)]

    f = MultiFernet(keys)
    token = f.encrypt(msg)

    # Build a second MultiFernet with a new primary key prepended, so the
    # original keys are still available for decryption of the source token.
    new_key = Fernet(Fernet.generate_key())
    f2 = MultiFernet([new_key] + keys)

    rotated = f2.rotate(token)

    # Property 1: The rotated token is always of type bytes.
    assert isinstance(rotated, bytes)

    # Property 2: Decrypting the rotated token yields the original plaintext.
    assert f2.decrypt(rotated) == msg

    # Property 3: The rotated token preserves the original timestamp.
    assert _extract_timestamp(rotated) == _extract_timestamp(token)

    # Property 4: The rotated token is valid URL-safe base64.
    # (Raises if not valid; round-trip confirms decodability.)
    decoded = base64.urlsafe_b64decode(rotated)
    assert base64.urlsafe_b64encode(decoded) == rotated

    # Property 5: Since the primary key changed (new_key is at front), the
    # rotated token differs from the input token, but decrypted contents match.
    assert rotated != token
    assert f2.decrypt(rotated) == f.decrypt(token)
# End program