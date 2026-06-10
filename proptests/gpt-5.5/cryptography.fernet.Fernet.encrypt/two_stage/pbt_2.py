from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, InvalidToken
import base64
import time


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_returns_bytes(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert isinstance(token, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_returns_urlsafe_base64(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    urlsafe_base64_chars = (
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        b"abcdefghijklmnopqrstuvwxyz"
        b"0123456789"
        b"-_="
    )
    assert all(byte in urlsafe_base64_chars for byte in token)

    decoded = base64.urlsafe_b64decode(token)
    assert isinstance(decoded, bytes)
    assert len(decoded) > 0


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_round_trips_with_same_key(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_token_contains_current_timestamp(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    before = int(time.time())
    token = f.encrypt(plaintext)
    after = int(time.time())

    decoded = base64.urlsafe_b64decode(token)
    timestamp = int.from_bytes(decoded[1:9], byteorder="big")

    assert before <= timestamp <= after


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_modified_token_fails_authentication(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)
    tampered = bytes([token[0] ^ 1]) + token[1:]

    try:
        f.decrypt(tampered)
    except InvalidToken:
        pass
    else:
        assert False


# End program