from cryptography.fernet import Fernet, MultiFernet
from hypothesis import given, strategies as st

# Test 1
@given(st.binary())
def test_property_base64_encoded_output(msg):
    key1 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1])
    token = f.rotate(msg)
    assert isinstance(token, bytes)

# Test 2
@given(st.binary())
def test_property_same_decrypted_message(msg):
    key1 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1])
    token = f.rotate(msg)
    decrypted_msg = key1.decrypt(token)
    assert decrypted_msg == msg

# Test 3
@given(st.binary())
def test_property_encrypts_with_primary_key(msg):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    token = f.rotate(msg)
    decrypted_msg = key1.decrypt(token)
    assert decrypted_msg == msg

# Test 4
@given(st.integers())
def test_property_raises_type_error_on_invalid_input(msg):
    key1 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1])
    try:
        f.rotate(msg)
    except Exception as e:
        assert isinstance(e, TypeError)

# Test 5
@given(st.binary())
def test_property_raises_invalid_token_exception_on_invalid_input(msg):
    invalid_key = bytes('InvalidKey', 'utf-8')
    key1 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1])
    try:
        f.rotate(invalid_key)
    except Exception as e:
        assert isinstance(e, cryptography.fernet.InvalidToken)