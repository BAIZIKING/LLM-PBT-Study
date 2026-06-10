from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Generate random string of bytes
byte_string = st.binary()

@given(byte_string)
def test_encrypt_property(data):
    # Generate a fresh fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Test if encrypt returns a Fernet token which is a bytes object
    token = f.encrypt(data)
    assert isinstance(token, bytes)
    
    
@given(byte_string)
def test_decrypt_property(data):
    # Generate a fresh fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Token generation and decryption
    token = f.encrypt(data)
    original_plaintext = f.decrypt(token)

    # Test if decrypting the token recovers the original plaintext
    assert original_plaintext == data

    # Test if invalid token leads to a InvalidToken exception
    with pytest.raises(InvalidToken):
        f.decrypt(token + b"extra bytes")
        
        
@given(byte_string)
def test_decrypt_with_ttl_property(data):
    import time

    # Generate a fresh fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Token generation
    token = f.encrypt(data)

    # Test decrypt with valid ttl
    original_plaintext = f.decrypt(token, ttl=60)
    assert original_plaintext == data

    # Test if expired token leads to a InvalidToken exception
    time.sleep(2)  # Sleep for 2 seconds to expire the token
    with pytest.raises(InvalidToken):
        f.decrypt(token, ttl=1)  # ttl less than sleep time


@given(byte_string, st.integers(min_value=0, max_value=10**6))
def test_encrypt_at_time_property(data, time):
    # Generate a fresh fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Test if encrypt_at_time returns a Fernet token which is a bytes object
    token_at_time = f.encrypt_at_time(data, time)
    assert isinstance(token_at_time, bytes)


@given(byte_string, st.integers(min_value=0, max_value=10**6))
def test_decrypt_at_time_property(data, time):
    # Generate a fresh fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Token generation at particular time and decryption at the same time
    token_at_time = f.encrypt_at_time(data, time)
    original_plaintext = f.decrypt_at_time(token_at_time, ttl=60, current_time=time)

    # Test if decrypting the token recovers the original plaintext
    assert original_plaintext == data

    # Test if expired token leads to a InvalidToken exception
    with pytest.raises(InvalidToken):
        f.decrypt_at_time(token_at_time, ttl=1, current_time=time+4)  # current time greater than ttl
# End program