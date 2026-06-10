from hypothesis import given, strategies as st
import cryptography
import cryptography.fernet
import pytest
import base64


_KEY = base64.urlsafe_b64encode(b"\x00" * 32)
_OTHER_KEY = base64.urlsafe_b64encode(b"\x01" * 32)


def _fernet():
    return cryptography.fernet.Fernet(_KEY)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_round_trips_to_original_plaintext(data):
    plaintext = data.draw(st.binary(max_size=4096))

    f = _fernet()
    token = f.encrypt(plaintext)

    assert f.decrypt(token) == plaintext


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_returns_bytes(data):
    plaintext = data.draw(st.binary(max_size=4096))

    f = _fernet()

    decrypted = f.decrypt(f.encrypt(plaintext))
    decrypted_empty = f.decrypt(f.encrypt(b""))

    assert isinstance(decrypted, bytes)
    assert isinstance(decrypted_empty, bytes)
    assert decrypted_empty == b""


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_accepts_equivalent_bytes_and_str_tokens(data):
    plaintext = data.draw(st.binary(max_size=4096))

    f = _fernet()
    token_as_bytes = f.encrypt(plaintext)
    token_as_str = token_as_bytes.decode("ascii")

    assert f.decrypt(token_as_bytes) == plaintext
    assert f.decrypt(token_as_str) == plaintext
    assert f.decrypt(token_as_bytes) == f.decrypt(token_as_str)


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_with_no_ttl_ignores_token_age(data):
    plaintext = data.draw(st.binary(max_size=4096))
    created_at = data.draw(st.integers(min_value=0, max_value=2**31 - 1))
    observed_now = data.draw(st.integers(min_value=0, max_value=2**31 - 1))

    f = _fernet()
    token = f.encrypt_at_time(plaintext, created_at)

    original_time = cryptography.fernet.time.time
    cryptography.fernet.time.time = lambda: observed_now
    try:
        assert f.decrypt(token, ttl=None) == plaintext
    finally:
        cryptography.fernet.time.time = original_time


@given(st.data())
def test_cryptography_fernet_Fernet_decrypt_invalid_tokens_raise_InvalidToken(data):
    plaintext = data.draw(st.binary(max_size=4096))
    invalid_case = data.draw(
        st.sampled_from(["malformed", "tampered", "wrong_key", "expired"])
    )

    f = _fernet()

    if invalid_case == "malformed":
        token = b"definitely-not-a-valid-fernet-token"
        with pytest.raises(cryptography.fernet.InvalidToken):
            f.decrypt(token)

    elif invalid_case == "tampered":
        token = f.encrypt(plaintext)
        raw_token = bytearray(base64.urlsafe_b64decode(token))
        index = data.draw(st.integers(min_value=0, max_value=len(raw_token) - 1))
        raw_token[index] ^= 1
        tampered_token = base64.urlsafe_b64encode(bytes(raw_token))

        with pytest.raises(cryptography.fernet.InvalidToken):
            f.decrypt(tampered_token)

    elif invalid_case == "wrong_key":
        other_f = cryptography.fernet.Fernet(_OTHER_KEY)
        token = other_f.encrypt(plaintext)

        with pytest.raises(cryptography.fernet.InvalidToken):
            f.decrypt(token)

    else:
        created_at = data.draw(st.integers(min_value=0, max_value=2**31 - 1))
        ttl = data.draw(st.integers(min_value=0, max_value=1000))
        current_time = created_at + ttl + 1
        token = f.encrypt_at_time(plaintext, created_at)

        original_time = cryptography.fernet.time.time
        cryptography.fernet.time.time = lambda: current_time
        try:
            with pytest.raises(cryptography.fernet.InvalidToken):
                f.decrypt(token, ttl=ttl)
        finally:
            cryptography.fernet.time.time = original_time


# End program