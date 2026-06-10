from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

@given(data=st.binary(max_size=1000))
def test_decrypt_output_type(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    plaintext = f.decrypt(token)
    assert isinstance(plaintext, bytes)

@given(data=st.binary(max_size=1000))
def test_decrypt_encrypt_roundtrip(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    plaintext = f.decrypt(token)
    assert plaintext == data

@given(data=st.binary(max_size=1000), wrong_key=st.binary(min_size=32, max_size=32))
def test_decrypt_wrong_key(data, wrong_key):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    f_wrong = Fernet(wrong_key)
    try:
        f_wrong.decrypt(token)
        assert False, "InvalidToken exception should have been raised"
    except InvalidToken:
        assert True

@given(data=st.binary(max_size=1000), ttl=st.integers(min_value=1, max_value=60))
def test_decrypt_expired_token(data, ttl):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt_at_time(data, int(time.time()) - ttl - 1)
    try:
        f.decrypt(token, ttl=ttl)
        assert False, "InvalidToken exception should have been raised"
    except InvalidToken:
        assert True

@given(data=st.binary(max_size=1000), ttl=st.integers(min_value=1, max_value=60), current_time=st.integers(min_value=0, max_value=int(time.time())))
def test_decrypt_at_time_expired_token(data, ttl, current_time):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt_at_time(data, current_time - ttl - 1)
    try:
        f.decrypt_at_time(token, ttl, current_time)
        assert False, "InvalidToken exception should have been raised"
    except InvalidToken:
        assert True
# End program