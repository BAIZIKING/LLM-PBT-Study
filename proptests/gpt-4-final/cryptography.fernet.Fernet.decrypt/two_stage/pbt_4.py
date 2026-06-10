from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

@given(st.binary(), st.binary())
def test_type_of_output(key, message):
    f = Fernet(key)
    token = f.encrypt(message)
    decrypted_message = f.decrypt(token)
    assert isinstance(decrypted_message, bytes)

@given(st.binary(), st.binary())
def test_authenticated_decrypted_output(key, message):
    f = Fernet(key)
    token = f.encrypt(message)
    decrypted_message = f.decrypt(token)
    assert decrypted_message == message

@given(st.binary(), st.binary())
def test_invalid_token_exception(key, message):
    f = Fernet(key)
    invalid_token = message  # Not a valid token
    try:
        f.decrypt(invalid_token)
    except InvalidToken:
        assert True
    except Exception:
        assert False

@given(st.binary(), st.binary(), st.integers(min_value=0))
def test_output_with_ttl_parameter(key, message, ttl):
    f = Fernet(key)
    token = f.encrypt(message)
    try:
        f.decrypt(token, ttl=ttl)
    except InvalidToken:
        assert True
    except Exception:
        assert False

@given(st.binary(), st.binary(), st.integers(min_value=0))
def test_output_on_decrypt_at_time_function(key, message, current_time):
    f = Fernet(key)
    token = f.encrypt_at_time(message, current_time)
    try:
        decrypted_message = f.decrypt_at_time(token, None, current_time)
        assert decrypted_message == message
    except Exception:
        assert False
# End program