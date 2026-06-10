from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import base64

# Summary: Generate both valid bytes inputs, including empty bytes and arbitrary binary payloads,
# and invalid non-bytes inputs such as str, int, None, bytearray, lists, and dicts.
# For bytes, check that encrypt returns bytes, produces URL-safe base64, and decrypt round-trips.
# For non-bytes, check that encrypt raises TypeError as documented.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    input_value = data.draw(
        st.one_of(
            st.binary(max_size=4096),
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=True, allow_infinity=True),
            st.text(max_size=1024),
            st.binary(max_size=1024).map(bytearray),
            st.lists(st.integers(min_value=0, max_value=255), max_size=128),
            st.dictionaries(st.text(max_size=32), st.integers(), max_size=32),
        )
    )

    fernet = Fernet(Fernet.generate_key())

    if isinstance(input_value, bytes):
        token = fernet.encrypt(input_value)

        assert isinstance(token, bytes)

        # Fernet tokens are documented as URL-safe base64-encoded bytes.
        base64.b64decode(token, altchars=b"-_", validate=True)

        # The encrypted token should decrypt back to the original plaintext.
        assert fernet.decrypt(token) == input_value
    else:
        try:
            fernet.encrypt(input_value)
        except TypeError:
            pass
        else:
            raise AssertionError("encrypt() should raise TypeError for non-bytes input")

# End program