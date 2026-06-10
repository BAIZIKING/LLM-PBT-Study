from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

@given(data=st.binary(max_size=1000))
def test_encrypt_output_is_bytes(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert isinstance(encrypted, bytes)

@given(data=st.binary(max_size=1000))
def test_encrypt_output_is_longer_than_input(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert len(encrypted) > len(data)

@given(data=st.binary(max_size=1000))
def test_encrypt_output_is_different_each_time(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted1 = fernet.encrypt(data)
    encrypted2 = fernet.encrypt(data)
    assert encrypted1 != encrypted2

@given(data=st.binary(max_size=1000))
def test_decrypt_of_encrypt_is_identity(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    decrypted = fernet.decrypt(encrypted)
    assert decrypted == data

@given(data=st.binary(max_size=1000))
def test_decrypt_with_different_key_raises_exception(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    fernet1 = Fernet(key1)
    fernet2 = Fernet(key2)
    encrypted = fernet1.encrypt(data)
    try:
        fernet2.decrypt(encrypted)
        assert False, "Expected InvalidToken exception"
    except InvalidToken:
        pass
# End program