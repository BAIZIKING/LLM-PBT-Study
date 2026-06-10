from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

@given(st.binary())
def test_rotate_behavior(data):
    # Generate two random keys for testing
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()
    
    # Initialize MultiFernet with both keys
    multi_fernet = MultiFernet([Fernet(key1), Fernet(key2)])
    
    # Encrypt the original data
    token = multi_fernet.encrypt(data)
    
    # Rotate the token 
    rotated_token = multi_fernet.rotate(token)
    
    # Make sure the rotated token is a bytes type object
    assert isinstance(rotated_token, bytes)

    # Make sure rotation does not lose the original data
    decrypted_data = multi_fernet.decrypt(rotated_token)
    assert decrypted_data == data

@given(st.text())
def test_rotate_with_string_input(data):
    # Generate two random keys
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()
    
    # Initialize MultiFernet with both keys
    multi_fernet = MultiFernet([Fernet(key1), Fernet(key2)])
    
    # Encrypt the original data
    token = multi_fernet.encrypt(data.encode())
    
    # Rotate the token 
    rotated_token = multi_fernet.rotate(token)
    assert isinstance(rotated_token, bytes)

    # Make sure rotation does not lose the original data
    decrypted_data = multi_fernet.decrypt(rotated_token)
    assert decrypted_data.decode() == data

@given(st.integers())
def test_rotate_with_invalid_input(data):
    import pytest
    from cryptography.fernet import InvalidToken

    # Generate two random keys
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()

    # Initialize MultiFernet with both keys
    multi_fernet = MultiFernet([Fernet(key1), Fernet(key2)])
    
    # Test the function with integer input 
    with pytest.raises(TypeError):
        rotated_token = multi_fernet.rotate(data)

    # Test the function with invalid token
    with pytest.raises(InvalidToken):
        rotated_token = multi_fernet.rotate(str(data).encode())