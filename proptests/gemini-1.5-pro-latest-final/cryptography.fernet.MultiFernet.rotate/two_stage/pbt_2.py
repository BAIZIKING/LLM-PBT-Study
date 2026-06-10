from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Define strategies for generating keys and messages
keys = st.binary(min_size=32, max_size=32)
messages = st.binary(max_size=1024)  # Limit message size to avoid potential overflows


@given(keys, keys, keys, messages)
def test_rotate_decryptable_with_new_key(key1, key2, key3, message):
    f1 = MultiFernet([Fernet(key1), Fernet(key2)])
    f2 = MultiFernet([Fernet(key3), Fernet(key1), Fernet(key2)])
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    decrypted = f2.decrypt(rotated)
    assert decrypted == message


@given(keys, keys, keys, messages)
def test_rotate_undecryptable_with_old_key(key1, key2, key3, message):
    f1 = MultiFernet([Fernet(key1), Fernet(key2)])
    f2 = MultiFernet([Fernet(key3), Fernet(key2)])  # Remove key1
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    with pytest.raises(InvalidToken):
        f1.decrypt(rotated)  # Should fail with old key


@given(keys, keys, keys, messages)
def test_rotate_preserves_timestamp(key1, key2, key3, message):
    f1 = MultiFernet([Fernet(key1), Fernet(key2)])
    f2 = MultiFernet([Fernet(key3), Fernet(key1), Fernet(key2)])
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    original_timestamp = Fernet(key1).extract_timestamp(token)
    rotated_timestamp = Fernet(key3).extract_timestamp(rotated)
    assert original_timestamp == rotated_timestamp


@given(keys, keys, keys, messages)
def test_rotate_different_ciphertext(key1, key2, key3, message):
    f1 = MultiFernet([Fernet(key1), Fernet(key2)])
    f2 = MultiFernet([Fernet(key3), Fernet(key1), Fernet(key2)])
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    assert token != rotated


@given(keys, keys, keys, messages)
def test_rotate_url_safe_base64(key1, key2, key3, message):
    f1 = MultiFernet([Fernet(key1), Fernet(key2)])
    f2 = MultiFernet([Fernet(key3), Fernet(key1), Fernet(key2)])
    token = f1.encrypt(message)
    rotated = f2.rotate(token)
    assert rotated.decode('ascii').isalnum()  # Check for URL-safe Base64 characters
# End program