from hypothesis import given, strategies as st
import base64
import re
import pytest
from cryptography.fernet import Fernet


# Property 1: Round-trip / Decryption inverse
@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_roundtrip():
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    assert f.decrypt(token) == data
# End program


# Property 2: Output type is always bytes
@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_output_type():
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    assert isinstance(token, bytes)
# End program


# Property 3: Output is valid URL-safe base64
@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_urlsafe_base64():
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    # Token only contains URL-safe base64 characters
    assert re.fullmatch(rb"[A-Za-z0-9_\-=]+", token) is not None
    # And it can be decoded as URL-safe base64 without error
    base64.urlsafe_b64decode(token)
# End program


# Property 4: Non-determinism / Uniqueness of tokens
@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_nondeterministic():
    key = Fernet.generate_key()
    f = Fernet(key)
    token1 = f.encrypt(data)
    token2 = f.encrypt(data)
    # Tokens embed an IV (and timestamp), so they should generally differ.
    assert token1 != token2
    # Both should still decrypt back to the original data.
    assert f.decrypt(token1) == data
    assert f.decrypt(token2) == data
# End program


# Property 5: TypeError on non-bytes input
@given(
    data=st.one_of(
        st.text(max_size=4096),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.none(),
        st.lists(st.integers(), max_size=100),
    )
)
def test_cryptography_fernet_Fernet_encrypt_type_error():
    key = Fernet.generate_key()
    f = Fernet(key)
    with pytest.raises(TypeError):
        f.encrypt(data)
# End program