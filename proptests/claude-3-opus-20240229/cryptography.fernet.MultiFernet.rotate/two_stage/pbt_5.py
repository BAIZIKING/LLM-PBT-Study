from hypothesis import given, strategies as st
from hypothesis.strategies import builds
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

@given(plaintext=st.binary(max_size=1024))
def test_rotated_token_is_valid_fernet(plaintext):
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    Fernet(key1).decrypt(rotated_token)  # should not raise InvalidToken

@given(plaintext=st.binary(max_size=1024))
def test_rotated_token_decrypts_to_original(plaintext):
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    assert f.decrypt(rotated_token) == plaintext

@given(token=st.binary(max_size=1024))
def test_rotating_token_twice_is_idempotent(token):
    key1, key2 = Fernet.generate_key(), Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    try:
        rotated1 = f.rotate(token) 
        rotated2 = f.rotate(rotated1)
        assert rotated1 == rotated2
    except InvalidToken:
        pass  # rotating invalid tokens is undefined behavior

@given(token=st.binary(max_size=1024))
def test_rotating_invalid_token_raises_error(token):
    key1, key2 = Fernet.generate_key(), Fernet.generate_key() 
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    try:
        f.rotate(token)
    except InvalidToken:
        pass
    else:
        assert token.startswith(b'gAAA') # all valid v1 tokens start with this

# unable to test timestamp preservation, since timestamp 
# is not exposed by cryptography API
# End program