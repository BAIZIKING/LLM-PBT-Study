from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Our strategy for generating Fernet tokens
def token_strategy():
    key = Fernet.generate_key()
    f = Fernet(key)
    return f.encrypt(st.binary().example().encode())

# Our strategy for generating ttl
ttl_strategy = st.none() | st.integers(min_value=1, max_value=10000)

@given(token=st.builds(token_strategy), ttl=ttl_strategy)
def test_decrypt_returns_original_message(token, ttl):
    """
    Test that decrypting an encrypted message returns the original message.
    """
    key = Fernet.generate_key()
    f = Fernet(key)
    original_message = b'original message'
    encrypted_message = f.encrypt(original_message)
    try:
        decrypted_message = f.decrypt(encrypted_message, ttl)
        assert decrypted_message == original_message
    except InvalidToken:
        assert ttl is not None

@given(token=st.builds(token_strategy))
def test_decrypt_returns_byte_string(token):
    """
    Test that the decrypt method always returns bytes.
    """
    key = Fernet.generate_key()
    f = Fernet(key)
    result = f.decrypt(token)
    assert isinstance(result, bytes)

@given(token=st.builds(token_strategy), ttl=ttl_strategy)
def test_decrypt_raises_for_invalid_token(token, ttl):
    """
    Test that an invalid token always raises InvalidToken.
    """
    key = Fernet.generate_key()
    f = Fernet(key)
    try:
        f.decrypt(token+b'invalid', ttl)
    except InvalidToken:
        return True
    assert False, "Expected InvalidToken to be raised"

@given(token=st.builds(token_strategy), ttl=st.integers(min_value=1, max_value=2))
def test_decrypt_raises_for_old_token(token, ttl):
    """
    Test that a token older than TTL always raises InvalidToken.
    """
    import time
    time.sleep(ttl)
    key = Fernet.generate_key()
    f = Fernet(key)
    try:
        f.decrypt(token, ttl)
    except InvalidToken:
        return True
    assert False, "Expected InvalidToken to be raised for old tokens"

@given(token=st.builds(token_strategy))
def test_decrypt_raises_for_non_bytes_or_str(token):
    """
    Test that a token that is not bytes or str always raises TypeError.
    """
    key = Fernet.generate_key()
    f = Fernet(key)
    try:
        f.decrypt(12345)
    except TypeError:
        return True
    assert False, "Expected TypeError to be raised"
# End program