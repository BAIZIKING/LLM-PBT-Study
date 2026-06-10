from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

@given(data=st.binary(max_size=1000))
def test_encrypt_output_is_bytes(data):
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
def test_encrypt_decrypt_roundtrip(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    decrypted = fernet.decrypt(encrypted)
    assert decrypted == data

@given(data=st.binary(max_size=1000))
def test_encrypt_decrypt_different_key(data):
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

@given(data=st.binary(max_size=1000))
def test_encrypt_output_is_url_safe(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    url_safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    assert all(c in url_safe_chars for c in encrypted.decode())
# End program