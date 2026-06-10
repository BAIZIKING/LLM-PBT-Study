from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, InvalidToken
import base64
import re
import time


_MAX_INPUT_SIZE = 4096
_URLSAFE_BASE64_RE = re.compile(rb"^[A-Za-z0-9_-]+={0,2}$")


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_returns_bytes(data):
    plaintext = data.draw(st.binary(max_size=_MAX_INPUT_SIZE))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert isinstance(token, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_returns_urlsafe_base64_token(data):
    plaintext = data.draw(st.binary(max_size=_MAX_INPUT_SIZE))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert _URLSAFE_BASE64_RE.fullmatch(token)
    decoded = base64.b64decode(token, altchars=b"-_", validate=True)
    assert isinstance(decoded, bytes)
    assert len(decoded) > 0


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_round_trips_with_same_key(data):
    plaintext = data.draw(st.binary(max_size=_MAX_INPUT_SIZE))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_token_rejects_tampering(data):
    plaintext = data.draw(st.binary(max_size=_MAX_INPUT_SIZE))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)
    index = data.draw(st.integers(min_value=0, max_value=len(token) - 1))

    tampered = bytearray(token)
    tampered[index] ^= 1
    tampered = bytes(tampered)

    try:
        f.decrypt(tampered)
        assert False, "Tampered token decrypted successfully"
    except InvalidToken:
        pass


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_token_contains_creation_time(data):
    plaintext = data.draw(st.binary(max_size=_MAX_INPUT_SIZE))
    key = Fernet.generate_key()
    f = Fernet(key)

    before = int(time.time())
    token = f.encrypt(plaintext)
    after = int(time.time())

    timestamp = f.extract_timestamp(token)

    assert before <= timestamp <= after
# End program