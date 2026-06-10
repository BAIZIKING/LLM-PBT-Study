from hypothesis import given, strategies as st
import cryptography.fernet as fernet
import time

# Generate valid Fernet keys and data
keys = st.binary(min_size=32, max_size=32)
data = st.binary()

# Generate valid TTL values
ttl_values = st.integers(min_value=1, max_value=3600)

@given(keys, data)
def test_decrypt_matches_original(key, data):
    f = fernet.Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert decrypted == data

@given(keys, data)
def test_invalid_key_raises_exception(key, data):
    wrong_key = fernet.Fernet.generate_key()
    f = fernet.Fernet(key)
    token = f.encrypt(data)
    with pytest.raises(fernet.InvalidToken):
        fernet.Fernet(wrong_key).decrypt(token)

@given(keys, data, ttl_values)
def test_expired_token_raises_exception(key, data, ttl):
    f = fernet.Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(data, current_time - ttl - 1)
    with pytest.raises(fernet.InvalidToken):
        f.decrypt(token, ttl=ttl)

@given(keys, data)
def test_decrypt_output_type(key, data):
    f = fernet.Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert isinstance(decrypted, bytes)

@given(keys, data)
def test_decrypt_idempotence(key, data):
    f = fernet.Fernet(key)
    token = f.encrypt(data)
    decrypted_once = f.decrypt(token)
    decrypted_twice = f.decrypt(token)
    assert decrypted_once == decrypted_twice
# End program