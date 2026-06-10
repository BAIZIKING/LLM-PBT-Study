from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, InvalidToken
import base64
import time
import pytest


def _fernet_from_raw_key(raw_key: bytes) -> Fernet:
    return Fernet(base64.urlsafe_b64encode(raw_key))


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_round_trip_property(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32))
    plaintext = data.draw(st.binary(max_size=2048))

    fernet = _fernet_from_raw_key(raw_key)
    token = fernet.encrypt(plaintext)

    assert fernet.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_returns_bytes_property(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32))
    plaintext = data.draw(st.binary(max_size=2048))

    fernet = _fernet_from_raw_key(raw_key)
    token = fernet.encrypt(plaintext)
    decrypted = fernet.decrypt(token)

    assert isinstance(decrypted, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_is_repeatable_property(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32))
    plaintext = data.draw(st.binary(max_size=2048))

    fernet = _fernet_from_raw_key(raw_key)
    token = fernet.encrypt(plaintext)

    first = fernet.decrypt(token)
    second = fernet.decrypt(token)

    assert first == second == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_bytes_and_str_tokens_match_property(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32))
    plaintext = data.draw(st.binary(max_size=2048))

    fernet = _fernet_from_raw_key(raw_key)
    token_as_bytes = fernet.encrypt(plaintext)
    token_as_str = token_as_bytes.decode("ascii")

    assert fernet.decrypt(token_as_bytes) == fernet.decrypt(token_as_str)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_ttl_property(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32))
    plaintext = data.draw(st.binary(max_size=2048))
    age = data.draw(st.integers(min_value=0, max_value=10_000))
    slack = data.draw(st.integers(min_value=100, max_value=10_000))

    fernet = _fernet_from_raw_key(raw_key)
    now = int(time.time())

    valid_token = fernet.encrypt_at_time(plaintext, now - age)
    assert fernet.decrypt(valid_token, ttl=age + slack) == plaintext

    expired_ttl = data.draw(st.integers(min_value=0, max_value=10_000))
    expired_token = fernet.encrypt_at_time(plaintext, now - expired_ttl - slack)

    with pytest.raises(InvalidToken):
        fernet.decrypt(expired_token, ttl=expired_ttl)


# End program