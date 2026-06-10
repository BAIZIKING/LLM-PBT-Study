from hypothesis import given, strategies as st
import cryptography.fernet as fernet

# Define a strategy for generating Fernet keys
keys_strategy = st.binary(min_size=32, max_size=32)

# Define a strategy for generating byte strings (messages)
message_strategy = st.binary()

@given(keys_strategy, keys_strategy, keys_strategy, message_strategy)
def test_cryptography_fernet_MultiFernet_rotate_property_1_and_2(key1, key2, key3, message):
    """
    Tests properties 1 and 2:
    1. Decryptability with new key
    2. Undecryptable with old key
    """
    f1 = fernet.MultiFernet([fernet.Fernet(key1), fernet.Fernet(key2)])
    f2 = fernet.MultiFernet([fernet.Fernet(key3), fernet.Fernet(key1)])
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    assert f2.decrypt(rotated) == message
    with pytest.raises(fernet.InvalidToken):
        f1.decrypt(rotated)

@given(keys_strategy, keys_strategy, message_strategy)
def test_cryptography_fernet_MultiFernet_rotate_property_3(key1, key2, message):
    """
    Tests property 3:
    3. Preserved timestamp
    """
    f = fernet.MultiFernet([fernet.Fernet(key1), fernet.Fernet(key2)])
    token = f.encrypt(message)
    rotated = f.rotate(token)
    # Extract timestamps from the token and rotated token
    timestamp_original = fernet.Fernet._get_unverified_token_data(token)[1]
    timestamp_rotated = fernet.Fernet._get_unverified_token_data(rotated)[1]
    assert timestamp_original == timestamp_rotated

@given(keys_strategy, keys_strategy, message_strategy)
def test_cryptography_fernet_MultiFernet_rotate_property_4(key1, key2, message):
    """
    Tests property 4:
    4. Output format (URL-safe base64-encoded bytes)
    """
    f = fernet.MultiFernet([fernet.Fernet(key1), fernet.Fernet(key2)])
    token = f.encrypt(message)
    rotated = f.rotate(token)
    # Check if the rotated token is URL-safe base64-encoded
    assert fernet.Fernet._is_valid_url_safe_token(rotated)

@given(keys_strategy, keys_strategy, message_strategy)
def test_cryptography_fernet_MultiFernet_rotate_property_5(key1, key2, message):
    """
    Tests property 5:
    5. Identical plaintext after decryption
    """
    f = fernet.MultiFernet([fernet.Fernet(key1), fernet.Fernet(key2)])
    token = f.encrypt(message)
    rotated = f.rotate(token)
    assert f.decrypt(token) == f.decrypt(rotated)
# End program