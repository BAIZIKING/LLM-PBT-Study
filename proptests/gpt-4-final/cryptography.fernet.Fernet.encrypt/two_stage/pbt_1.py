from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

st_key = st.binary(min_size=32, max_size=32)
st_data = st.binary(min_size=1, max_size=100)
st_ttl = st.integers(min_value=0, max_value=3600)

@given(st_key, st_data)
def test_encrypt_decrypt_property(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted_data = f.decrypt(token)
    assert data == decrypted_data

@given(st_data)
def test_different_key_property(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f1 = Fernet(key1)
    f2 = Fernet(key2)
    token = f1.encrypt(data)
    try:
       f2.decrypt(token)
    except cryptography.fernet.InvalidToken:
        assert True
    else:
        assert False

@given(st_key, st.text())
def test_type_error_property(key, data):
    f = Fernet(key)
    try:
        f.encrypt(data)
    except TypeError:
        assert True
    else:
        assert False

@given(st_key, st_data, st_ttl)
def test_ttl_property(key, data, ttl):
    f = Fernet(key)
    token = f.encrypt(data)
    try:
        time.sleep(ttl + 1)
        f.decrypt(token, ttl=ttl)
    except cryptography.fernet.InvalidToken:
        assert True
    else:
        assert False

@given(st_key, st_data)
def test_url_safety_property(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    assert binascii.a2b_base64(binascii.b2a_base64(token)) == token