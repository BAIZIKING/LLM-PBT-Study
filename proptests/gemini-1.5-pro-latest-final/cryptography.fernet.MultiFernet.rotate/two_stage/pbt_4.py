from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Define a strategy for generating Fernet keys
keys_strategy = st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5)

# Define a strategy for generating byte strings 
byte_strings = st.binary(max_size=1024) # Limit size to avoid potential overflows

@given(keys_strategy, byte_strings)
def test_fernet_rotate_output_format(keys, data):
    """Tests that the output is a URL-safe base64 encoded byte string."""
    f = MultiFernet([Fernet(key) for key in keys])
    token = f.encrypt(data)
    rotated = f.rotate(token)
    assert isinstance(rotated, bytes)
    assert all(c in b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in rotated)

@given(keys_strategy, byte_strings)
def test_fernet_rotate_decryptability(keys, data):
    """Tests that rotated token can be decrypted using the primary key."""
    f = MultiFernet([Fernet(key) for key in keys])
    primary_key = f._fernets[0]
    token = f.encrypt(data)
    rotated = f.rotate(token)
    decrypted = primary_key.decrypt(rotated)
    assert decrypted == data

@given(keys_strategy, byte_strings)
def test_fernet_rotate_tamper_detection(keys, data):
    """Tests that modifying the token causes decryption failure."""
    f = MultiFernet([Fernet(key) for key in keys])
    token = f.encrypt(data)
    rotated = f.rotate(token)
    # Modify a single byte
    tampered_token = rotated[:-1] + b'a' 
    with pytest.raises(InvalidToken):
        f.decrypt(tampered_token)

@given(keys_strategy, byte_strings)
def test_fernet_rotate_determinism(keys, data):
    """Tests that rotating the same token produces the same output."""
    f = MultiFernet([Fernet(key) for key in keys])
    token = f.encrypt(data)
    rotated1 = f.rotate(token)
    rotated2 = f.rotate(token)
    assert rotated1 == rotated2

@given(keys_strategy, byte_strings)
def test_fernet_rotate_timestamp_preservation(keys, data):
    """Tests that the timestamp is preserved in the rotated token."""
    # This test assumes Fernet token structure and might need adjustments 
    # depending on the internal implementation details of Fernet.

    f = MultiFernet([Fernet(key) for key in keys])
    token = f.encrypt(data)
    rotated = f.rotate(token)
    original_timestamp = token.split(b'.')[1]
    rotated_timestamp = rotated.split(b'.')[1]
    assert original_timestamp == rotated_timestamp 
# End program