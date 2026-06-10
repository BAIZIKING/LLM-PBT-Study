from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

# Define strategies for key generation and data
key_strategy = st.binary(min_size=32, max_size=32)
data_strategy = st.binary()
ttl_strategy = st.integers(min_value=1)  # Ensure TTL is at least 1 second

# Property 1: Decrypted data matches original data
@given(key_strategy, data_strategy)
def test_fernet_decrypt_matches_original(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert decrypted == data

# Property 2: Invalid token raises exception
@given(key_strategy, st.binary())
def test_fernet_decrypt_invalid_token(key, invalid_token):
    f = Fernet(key)
    with pytest.raises(InvalidToken):
        f.decrypt(invalid_token)

# Property 3: Decryption is deterministic
@given(key_strategy, data_strategy)
def test_fernet_decrypt_deterministic(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted1 = f.decrypt(token)
    decrypted2 = f.decrypt(token)
    assert decrypted1 == decrypted2

# Property 4: TTL enforces time-based expiration
@given(key_strategy, data_strategy, ttl_strategy)
def test_fernet_decrypt_ttl_expiration(key, data, ttl):
    current_time = int(time.time())
    f = Fernet(key)
    token = f.encrypt_at_time(data, current_time)
    # Test with expired token
    with pytest.raises(InvalidToken):
        f.decrypt_at_time(token, ttl, current_time + ttl + 1)
    # Test with valid token (within TTL)
    decrypted = f.decrypt_at_time(token, ttl, current_time + ttl)
    assert decrypted == data

# Property 5: Decryption is independent of key generation method
@given(key_strategy, data_strategy)
def test_fernet_decrypt_key_independence(key, data):
    f1 = Fernet(Fernet.generate_key())
    f2 = Fernet(key)
    token = f1.encrypt(data)
    decrypted1 = f1.decrypt(token)
    decrypted2 = f2.decrypt(token)
    assert decrypted1 == decrypted2 == data 
# End program