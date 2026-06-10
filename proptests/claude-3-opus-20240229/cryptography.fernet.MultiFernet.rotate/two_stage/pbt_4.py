from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

@given(st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=5, unique=True))
def test_cryptography_fernet_MultiFernet_rotate_output_type(keys):
    multi_fernet = MultiFernet([Fernet(key) for key in keys])
    token = multi_fernet.encrypt(b"test message")
    rotated_token = multi_fernet.rotate(token)
    assert isinstance(rotated_token, bytes)

@given(st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5, unique=True), st.binary())
def test_cryptography_fernet_MultiFernet_rotate_decryption(keys, message):
    multi_fernet = MultiFernet([Fernet(key) for key in keys])
    token = multi_fernet.encrypt(message)
    rotated_token = multi_fernet.rotate(token)
    assert multi_fernet.decrypt(rotated_token) == message

@given(st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5, unique=True), st.binary())
def test_cryptography_fernet_MultiFernet_rotate_timestamp(keys, message):
    multi_fernet = MultiFernet([Fernet(key) for key in keys])
    token = multi_fernet.encrypt(message)
    rotated_token = multi_fernet.rotate(token)
    assert Fernet._get_unverified_token_data(token)[:4] == Fernet._get_unverified_token_data(rotated_token)[:4]

@given(st.lists(st.binary(min_size=32, max_size=32), min_size=2, max_size=5, unique=True), st.binary())
def test_cryptography_fernet_MultiFernet_rotate_decryption_equivalence(keys, message):
    multi_fernet = MultiFernet([Fernet(key) for key in keys])
    token = multi_fernet.encrypt(message)
    rotated_token = multi_fernet.rotate(token)
    assert multi_fernet.decrypt(token) == multi_fernet.decrypt(rotated_token)

@given(st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=5, unique=True), st.binary())
def test_cryptography_fernet_MultiFernet_rotate_invalid_token(keys, invalid_token):
    multi_fernet = MultiFernet([Fernet(key) for key in keys])
    try:
        multi_fernet.rotate(invalid_token)
    except InvalidToken:
        assert True
    except Exception:
        assert False
    else:
        assert False
# End program