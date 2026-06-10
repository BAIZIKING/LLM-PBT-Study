from hypothesis import given, strategies as st
import base64
from cryptography.fernet import Fernet


@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_returns_bytes(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    assert isinstance(token, bytes)


@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_url_safe_base64(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    # Should only contain URL-safe base64 characters and decode successfully
    allowed = set(
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
    )
    assert set(token).issubset(allowed)
    # Should be decodable as URL-safe base64
    decoded = base64.urlsafe_b64decode(token)
    assert isinstance(decoded, bytes)


@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_roundtrip(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    assert f.decrypt(token) == data


@given(data=st.binary(max_size=4096))
def test_cryptography_fernet_Fernet_encrypt_non_deterministic(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token1 = f.encrypt(data)
    token2 = f.encrypt(data)
    assert token1 != token2


@given(
    data=st.one_of(
        st.text(max_size=4096),
        st.integers(),
        st.none(),
        st.lists(st.integers(), max_size=100),
        st.floats(allow_nan=True, allow_infinity=True),
    )
)
def test_cryptography_fernet_Fernet_encrypt_type_error(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    try:
        f.encrypt(data)
        assert False, "Expected TypeError for non-bytes input"
    except TypeError:
        pass
# End program