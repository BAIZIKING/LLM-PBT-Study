from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, InvalidToken
import base64
import time


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_property_1(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert isinstance(token, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_property_2(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    decoded = base64.urlsafe_b64decode(token)
    assert base64.urlsafe_b64encode(decoded) == token
    assert all(
        byte in b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
        for byte in token
    )


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_property_3(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_property_4(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    token = f.encrypt(plaintext)
    index = data.draw(st.integers(min_value=0, max_value=len(token) - 1))

    modified_token = bytearray(token)
    modified_token[index] ^= 1

    try:
        f.decrypt(bytes(modified_token))
    except InvalidToken:
        pass
    else:
        assert False


@given(st.data())
def test_cryptography_fernet_Fernet_encrypt_property_5(data):
    plaintext = data.draw(st.binary(max_size=4096))
    key = Fernet.generate_key()
    f = Fernet(key)

    before = int(time.time())
    token = f.encrypt(plaintext)
    after = int(time.time())

    decoded = base64.urlsafe_b64decode(token)
    timestamp = int.from_bytes(decoded[1:9], byteorder="big")

    assert before <= timestamp <= after


# End program