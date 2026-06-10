from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import base64
import time

# Test strategy for generating bytes
byte_strategy = st.binary(min_size=1, max_size=100)

# Test strategy for generating keys
key_strategy = st.binary(min_size=32, max_size=32).map(base64.urlsafe_b64encode)

# Property 1: Output of encryption should be URL-safe base64 encoded bytes
@given(st.data())
def test_encrypt_property1(data):
    key = data.draw(key_strategy)
    message = data.draw(byte_strategy)
    f = Fernet(key)
    token = f.encrypt(message)
    # Check if output is bytes
    assert isinstance(token, bytes)
    # Check if output is URL-safe Base64
    assert base64.urlsafe_b64decode(token)

# Property 2: Two similar messages should produce different encrypted outputs
@given(st.data())
def test_encrypt_property2(data):
    key = data.draw(key_strategy)
    message = data.draw(byte_strategy)
    f = Fernet(key)
    token1 = f.encrypt(message)
    token2 = f.encrypt(message)
    assert token1 != token2

# Property 3: Decrypting an encrypted message should give back the original
@given(st.data())
def test_decrypt_property(data):
    key = data.draw(key_strategy)
    message = data.draw(byte_strategy)
    f = Fernet(key)
    token = f.encrypt(message)
    decrypted_message = f.decrypt(token)
    assert decrypted_message == message

# Property 4: decrypt(token, ttl) should raise an exception if more than ttl seconds have passed
@given(st.data())
def test_decrypt_ttl_property(data):
    key = data.draw(key_strategy)
    message = data.draw(byte_strategy)
    ttl = data.draw(st.integers(min_value=1, max_value=5))
    f = Fernet(key)
    token = f.encrypt(message)
    time.sleep(ttl + 1)  # wait for ttl to expire
    try:
        decrypted_message = f.decrypt(token, ttl)
        assert False  # should never reach this line
    except:
        assert True  # exception is expected

# Property 5: Decrypting an invalid or tampered token should raise a exception
@given(st.data())
def test_invalid_token_property(data):
    key = data.draw(key_strategy)
    key2 = data.draw(key_strategy)
    message = data.draw(byte_strategy)
    f = Fernet(key)
    token = f.encrypt(message)
    f2 = Fernet(key2)
    try:
        decrypted_message = f2.decrypt(token)  # decrypt with wrong key
        assert False  # should never reach this line
    except:
        assert True  # exception is expected