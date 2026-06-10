from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import base64
import pytest

# Summary: Generate both valid bytes inputs and invalid non-bytes inputs. Bytes include empty data,
# small examples, arbitrary binary data with any byte values, and larger payloads. Non-bytes include
# strings, integers, None, bytearray, memoryview, and lists. For bytes, check encrypt returns bytes,
# produces URL-safe base64-decodable Fernet tokens, and decrypting the token round-trips to the
# original plaintext. For non-bytes, check encrypt raises TypeError as documented.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    plaintext_or_invalid = data.draw(
        st.one_of(
            st.binary(min_size=0, max_size=4096),
            st.sampled_from([b"", b"\x00", b"\xff", b"hello", bytes(range(256))]),
            st.text(),
            st.integers(),
            st.none(),
            st.builds(bytearray, st.binary(min_size=0, max_size=128)),
            st.builds(memoryview, st.binary(min_size=0, max_size=128)),
            st.lists(st.integers(min_value=0, max_value=255), max_size=128),
        )
    )

    f = Fernet(Fernet.generate_key())

    if isinstance(plaintext_or_invalid, bytes):
        token = f.encrypt(plaintext_or_invalid)

        assert isinstance(token, bytes)
        base64.urlsafe_b64decode(token)
        assert f.decrypt(token) == plaintext_or_invalid
    else:
        with pytest.raises(TypeError):
            f.encrypt(plaintext_or_invalid)

# End program