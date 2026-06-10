from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Define a strategy for generating Fernet keys
keys = st.binary(min_size=32, max_size=32)

# Strategy for generating input data within reasonable size limits
data = st.binary(max_size=1024)

@given(keys, data)
def test_fernet_encrypt_output_is_bytes(key, data):
    f = Fernet(key)
    encrypted = f.encrypt(data)
    assert isinstance(encrypted, bytes)

@given(keys, data)
def test_fernet_encrypt_output_length(key, data):
    f = Fernet(key)
    encrypted = f.encrypt(data)
    assert len(encrypted) > len(data)

@given(keys, data)
def test_fernet_encrypt_output_is_urlsafe_base64(key, data):
    f = Fernet(key)
    encrypted = f.encrypt(data)
    # Check if all characters are within the URL-safe Base64 alphabet
    assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in encrypted.decode())

@given(keys, data)
def test_fernet_encrypt_determinism(key, data):
    f = Fernet(key)
    encrypted1 = f.encrypt(data)
    encrypted2 = f.encrypt(data)
    assert encrypted1 == encrypted2

@given(data, st.tuples(keys, keys))
def test_fernet_encrypt_different_keys(data, keys):
    key1, key2 = keys
    f1 = Fernet(key1)
    f2 = Fernet(key2)
    encrypted1 = f1.encrypt(data)
    encrypted2 = f2.encrypt(data)
    assert encrypted1 != encrypted2
# End program