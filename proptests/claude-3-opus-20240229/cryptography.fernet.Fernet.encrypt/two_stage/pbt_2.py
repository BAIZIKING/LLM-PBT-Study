from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(data=st.binary(max_size=1000))
def test_encrypt_output_type(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert isinstance(encrypted, bytes)

@given(data=st.binary(max_size=1000))
def test_encrypt_output_length(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert len(encrypted) > len(data)

@given(data=st.binary(max_size=1000))
def test_encrypt_output_different(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted1 = fernet.encrypt(data)
    encrypted2 = fernet.encrypt(data)
    assert encrypted1 != encrypted2

@given(data=st.just(b''))
def test_encrypt_empty_input(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    assert len(encrypted) > 0

@given(data=st.binary(max_size=1000))
def test_decrypt_encrypted_data(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    decrypted = fernet.decrypt(encrypted)
    assert decrypted == data
# End program