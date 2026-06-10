from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

# Define key generation strategy (avoiding very large values)
key_strategy = st.binary(min_size=32, max_size=32)

# Data strategy with limitations for size and type
data_strategy = st.binary(max_size=1024)  # Limit data size to avoid slow tests and potential overflows

# Timestamp strategy within reasonable bounds
time_strategy = st.integers(min_value=1, max_value=2**32 - 1)  # Limit timestamp range to avoid overflows


@given(key_strategy, data_strategy)
def test_fernet_decrypt_after_encrypt(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted_data = f.decrypt(token)
    assert decrypted_data == data
# End program

@given(key_strategy, data_strategy)
def test_fernet_immutability(key, data):
    f = Fernet(key)
    original_data = data[:]  # Create a copy to compare later
    token = f.encrypt(data)
    _ = f.decrypt(token)  # We only care about side effects on 'data'
    assert data == original_data 
# End program

@given(key_strategy, data_strategy)
def test_fernet_token_format(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    # Check if base64 encoded and URL-safe
    assert token.isalnum() or any(c in b"-_" for c in token) 
# End program

@given(key_strategy, data_strategy, time_strategy, time_strategy)
def test_fernet_encrypt_at_time_dependence(key, data, time1, time2):
    f = Fernet(key)
    token1 = f.encrypt_at_time(data, time1)
    token2 = f.encrypt_at_time(data, time2)
    assert (time1 != time2) == (token1 != token2)  # Tokens differ if times differ
# End program

@given(key_strategy, data_strategy, time_strategy, st.integers(min_value=0))
def test_fernet_decrypt_ttl_dependence(key, data, current_time, ttl):
    f = Fernet(key)
    token = f.encrypt_at_time(data, current_time - ttl - 1)  # Create an expired token
    
    # Assert that decrypting an expired token raises an exception
    with pytest.raises(InvalidToken):
        f.decrypt_at_time(token, ttl, current_time)
# End program