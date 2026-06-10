from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, InvalidToken
import base64


def _draw_fernet(data):
    raw_key = data.draw(st.binary(min_size=32, max_size=32), label="raw_key")
    key = base64.urlsafe_b64encode(raw_key)
    return Fernet(key)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_round_trips_plaintext(data):
    f = _draw_fernet(data)
    plaintext = data.draw(st.binary(max_size=4096), label="plaintext")

    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_success_returns_bytes(data):
    f = _draw_fernet(data)
    plaintext = data.draw(st.binary(max_size=4096), label="plaintext")

    token = f.encrypt(plaintext)
    decrypted = f.decrypt(token)

    assert isinstance(decrypted, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_bytes_and_str_tokens_match(data):
    f = _draw_fernet(data)
    plaintext = data.draw(st.binary(max_size=4096), label="plaintext")

    token_as_bytes = f.encrypt(plaintext)
    token_as_str = token_as_bytes.decode("ascii")

    assert f.decrypt(token_as_bytes) == f.decrypt(token_as_str)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_without_ttl_ignores_token_age(data):
    f = _draw_fernet(data)
    plaintext = data.draw(st.binary(max_size=4096), label="plaintext")
    timestamp = data.draw(st.integers(min_value=0, max_value=2**31 - 1), label="timestamp")

    token = f.encrypt_at_time(plaintext, timestamp)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_ttl_accepts_fresh_and_rejects_expired(data):
    f = _draw_fernet(data)
    plaintext = data.draw(st.binary(max_size=4096), label="plaintext")
    valid_ttl = data.draw(st.integers(min_value=3600, max_value=86400), label="valid_ttl")
    expired_ttl = data.draw(st.integers(min_value=0, max_value=86400), label="expired_ttl")

    fresh_token = f.encrypt(plaintext)
    assert f.decrypt(fresh_token, ttl=valid_ttl) == plaintext

    expired_token = f.encrypt_at_time(plaintext, 0)
    try:
        f.decrypt(expired_token, ttl=expired_ttl)
    except InvalidToken:
        pass
    else:
        raise AssertionError("Expired token decrypted successfully")


# End program