from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

# Define a strategy for generating valid Fernet keys
keys = st.binary(min_size=32, max_size=32)

# Define a strategy for generating byte strings
data = st.binary()

# Define a strategy for generating TTL values (optional)
ttls = st.integers(min_value=1) 

@given(keys, data)
def test_decrypt_length_equals_plaintext_length(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    plaintext = f.decrypt(token)
    assert len(plaintext) == len(data)

@given(keys, data)
def test_decrypt_with_original_key_recovers_plaintext(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    plaintext = f.decrypt(token)
    assert plaintext == data

@given(keys, data, st.binary(min_size=32, max_size=32))
def test_decrypt_with_incorrect_key_fails(key, data, wrong_key):
    f = Fernet(key)
    token = f.encrypt(data)
    f_wrong = Fernet(wrong_key)
    with pytest.raises(InvalidToken):
        f_wrong.decrypt(token)

@given(keys, data, ttls)
def test_ttl_expiration_leads_to_decryption_failure(key, data, ttl):
    f = Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(data, current_time)
    # Wait for TTL to expire
    time.sleep(ttl + 1)
    with pytest.raises(InvalidToken):
        f.decrypt(token, ttl=ttl)

@given(keys, data)
def test_tampered_ciphertext_leads_to_decryption_failure(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    # Tamper with the token by flipping a bit
    tampered_token = bytearray(token)
    tampered_token[0] ^= 1
    with pytest.raises(InvalidToken):
        f.decrypt(bytes(tampered_token))

# End program