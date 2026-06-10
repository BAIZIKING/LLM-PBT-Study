from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

# Define strategies for key generation and data
key_strategy = st.binary(min_size=32, max_size=32)
data_strategy = st.binary(max_size=1024)  # Limit data size to avoid overflow

# Property 1: Decrypted output matches original input
@given(key_strategy, data_strategy)
def test_decrypt_matches_original(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert decrypted == data

# Property 2: Decryption fails with incorrect key
@given(key_strategy, data_strategy, key_strategy)
def test_decrypt_fails_with_wrong_key(key1, data, key2):
    f1 = Fernet(key1)
    token = f1.encrypt(data)
    f2 = Fernet(key2)
    with pytest.raises(InvalidToken):
        f2.decrypt(token)

# Property 3: Tampering with token causes decryption failure
@given(key_strategy, data_strategy)
def test_decrypt_fails_with_tampered_token(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    tampered_token = bytearray(token)
    tampered_token[0] ^= 0xFF  # Modify a byte
    with pytest.raises(InvalidToken):
        f.decrypt(tampered_token)

# Property 4: Expired tokens fail to decrypt (TTL test)
@given(key_strategy, data_strategy, st.integers(min_value=1, max_value=60))
def test_decrypt_fails_with_expired_token(key, data, ttl):
    f = Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(data, current_time)
    # Wait for token to expire
    time.sleep(ttl + 1)
    with pytest.raises(InvalidToken):
        f.decrypt(token, ttl=ttl)

# Property 5: Length of decrypted data matches original data
@given(key_strategy, data_strategy)
def test_decrypt_length_matches_original(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert len(decrypted) == len(data)
# End program