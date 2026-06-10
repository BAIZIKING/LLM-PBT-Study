from cryptography.fernet import Fernet
from hypothesis import given, strategies as st
import base64
import time

# Strategy for getting valid Fernet keys
fernet_keys = st.binary(min_size=32, max_size=32).map(base64.urlsafe_b64encode)

@given(st.binary(), fernet_keys)
def test_fernet_encrypt_output(data, key):
    f = Fernet(key)
    token = f.encrypt(data)
    assert token is not None
    assert isinstance(token, bytes)
    # check if the token is URL-safe base64-encoded
    assert token == base64.urlsafe_b64encode(base64.urlsafe_b64decode(token))

@given(st.binary(), fernet_keys)
def test_fernet_encrypt_decrypt(data, key):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted_data = f.decrypt(token)
    assert decrypted_data == data

@given(st.binary(), fernet_keys, st.integers(min_value=0))
def test_fernet_encrypt_decrypt_at_time(data, key, current_time):
    f = Fernet(key)
    token = f.encrypt_at_time(data, current_time)
    decrypted_data = f.decrypt_at_time(token, None, current_time)
    assert decrypted_data == data

@given(st.binary(), fernet_keys, st.integers(min_value=1))
def test_fernet_decrypt_ttl_expiry(data, key, ttl):
    f = Fernet(key)
    token = f.encrypt(data)
    time.sleep(ttl)
    try:
        f.decrypt(token, ttl)
        assert False # An exception should have been raised
    except cryptography.fernet.InvalidToken:
        assert True

@given(st.text(), fernet_keys)
def test_fernet_decrypt_with_invalid_token(invalid_token, key):
    f = Fernet(key)
    try:
        f.decrypt(invalid_token.encode())
        assert False # An exception should have been raised
    except (cryptography.fernet.InvalidToken,TypeError):
        assert True