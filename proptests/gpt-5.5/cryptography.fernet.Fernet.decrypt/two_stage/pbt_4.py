from hypothesis import given, strategies as st
import cryptography
import cryptography.fernet
import time
import pytest

@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_property_1(data):
    plaintext = data.draw(st.binary(max_size=4096))

    key = cryptography.fernet.Fernet.generate_key()
    f = cryptography.fernet.Fernet(key)

    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_property_2(data):
    plaintext = data.draw(st.binary(max_size=4096))

    key = cryptography.fernet.Fernet.generate_key()
    f = cryptography.fernet.Fernet(key)

    token = f.encrypt(plaintext)
    decrypted = f.decrypt(token)

    assert isinstance(decrypted, bytes)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_property_3(data):
    plaintext = data.draw(st.binary(max_size=4096))

    key = cryptography.fernet.Fernet.generate_key()
    f = cryptography.fernet.Fernet(key)

    token_as_bytes = f.encrypt(plaintext)
    token_as_str = token_as_bytes.decode("ascii")

    assert f.decrypt(token_as_bytes) == f.decrypt(token_as_str)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_property_4(data):
    plaintext = data.draw(st.binary(max_size=4096))

    key = cryptography.fernet.Fernet.generate_key()
    f = cryptography.fernet.Fernet(key)

    old_timestamp = 0
    token = f.encrypt_at_time(plaintext, old_timestamp)

    assert f.decrypt(token, ttl=None) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_property_5(data):
    plaintext = data.draw(st.binary(max_size=4096))
    ttl = data.draw(st.integers(min_value=1, max_value=3600))

    key = cryptography.fernet.Fernet.generate_key()
    f = cryptography.fernet.Fernet(key)

    current_time = int(time.time())

    valid_token = f.encrypt_at_time(plaintext, current_time)
    assert f.decrypt(valid_token, ttl=ttl) == plaintext

    expired_token = f.encrypt_at_time(plaintext, current_time - ttl - 2)
    with pytest.raises(cryptography.fernet.InvalidToken):
        f.decrypt(expired_token, ttl=ttl)

# End program