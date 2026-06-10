from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

@given(st.binary(max_size=1024))
def test_decrypt_output_type(plaintext):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(plaintext)
    decrypted = f.decrypt(token)
    assert isinstance(decrypted, bytes)

@given(st.binary(max_size=1024))
def test_decrypt_roundtrip(plaintext):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(plaintext)
    decrypted = f.decrypt(token)
    assert decrypted == plaintext

@given(st.binary(max_size=1024), st.integers(min_value=0, max_value=86400))
def test_decrypt_valid_ttl(plaintext, ttl):
    key = Fernet.generate_key()
    f = Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(plaintext, current_time)
    f.decrypt_at_time(token, ttl, current_time + ttl)

@given(st.binary(max_size=1024), st.integers(min_value=1, max_value=86400))
def test_decrypt_expired_ttl(plaintext, ttl):
    key = Fernet.generate_key()
    f = Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(plaintext, current_time - ttl - 1)
    try:
        f.decrypt_at_time(token, ttl, current_time)
        assert False
    except InvalidToken:
        pass

@given(st.binary(max_size=1024))
def test_decrypt_invalid_token(plaintext):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(plaintext)
    try:
        f.decrypt(token[:-1])
        assert False
    except InvalidToken:
        pass
# End program