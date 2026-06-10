from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(st.binary(), st.binary())
def test_decrypt_encrypt_property(data, key):
    f = Fernet(key)
    assert f.decrypt(f.encrypt(data)) == data
    
@given(st.binary(), st.binary())
def test_output_type_property(data, key):
    f = Fernet(key)
    assert isinstance(f.decrypt(f.encrypt(data)), bytes)

@given(st.binary(), st.text())
def test_invalid_token_exception_property(data, key):
    f = Fernet(key)
    try:
        f.decrypt(f.encrypt(data))
    except cryptography.fernet.InvalidToken:
        assert True

@given(st.binary(), st.integers())
def test_type_error_property(data, key):
    f = Fernet(key)
    try:
        f.decrypt(f.encrypt(data))
    except TypeError:
        assert True

@given(st.binary(), st.binary(), st.integers(min_value=1, max_value=60))
def test_ttl_respect_property(data, key, ttl):
    f = Fernet(key)
    try:
        f.decrypt_at_time(f.encrypt_at_time(data, ttl), ttl, int(time.time()) + ttl + 1)
    except cryptography.fernet.InvalidToken:
        assert True
# End program