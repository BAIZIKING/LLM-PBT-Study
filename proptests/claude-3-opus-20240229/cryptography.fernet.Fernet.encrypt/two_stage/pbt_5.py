from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

@given(st.binary(max_size=1000))
def test_encrypt_output_is_bytes(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert isinstance(encrypted, bytes)

@given(st.binary(max_size=1000))
def test_encrypt_output_is_different(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted1 = fernet.encrypt(data)
    encrypted2 = fernet.encrypt(data)
    assert encrypted1 != encrypted2

@given(st.binary(max_size=1000))
def test_decrypt_encrypt_roundtrip(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    decrypted = fernet.decrypt(encrypted)
    assert decrypted == data

@given(st.binary(max_size=1000))
def test_encrypt_output_length(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert len(encrypted) > len(data)

@given(st.one_of(st.text(max_size=1000), st.integers(), st.none()))
def test_encrypt_invalid_input_type(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    try:
        fernet.encrypt(data)
        assert False, "Expected TypeError"
    except TypeError:
        pass
# End program