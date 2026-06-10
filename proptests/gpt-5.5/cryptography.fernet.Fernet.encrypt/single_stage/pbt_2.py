from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import pytest

# Summary: Generate both valid bytes inputs, including empty bytes, arbitrary binary data, and varied sizes, plus invalid non-bytes inputs such as None, strings, integers, lists, dictionaries, and bytearrays. For bytes, check that encryption returns a URL-safe base64 bytes token, decrypts back to the original plaintext, and rejects tampering. For non-bytes, check that encrypt raises TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    valid_bytes = st.binary(min_size=0, max_size=4096)

    invalid_non_bytes = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.text(max_size=4096),
        st.lists(st.integers(), max_size=32),
        st.dictionaries(st.text(max_size=32), st.integers(), max_size=32),
        st.binary(min_size=0, max_size=4096).map(bytearray),
    )

    value = data.draw(st.one_of(valid_bytes, invalid_non_bytes))

    fernet = Fernet(Fernet.generate_key())

    if isinstance(value, bytes):
        token = fernet.encrypt(value)

        assert isinstance(token, bytes)
        assert fernet.decrypt(token) == value

        urlsafe_base64_chars = (
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            b"abcdefghijklmnopqrstuvwxyz"
            b"0123456789-_="
        )
        assert all(byte in urlsafe_base64_chars for byte in token)

        tampered_token = bytes([token[0] ^ 1]) + token[1:]
        with pytest.raises(InvalidToken):
            fernet.decrypt(tampered_token)
    else:
        with pytest.raises(TypeError):
            fernet.encrypt(value)
# End program