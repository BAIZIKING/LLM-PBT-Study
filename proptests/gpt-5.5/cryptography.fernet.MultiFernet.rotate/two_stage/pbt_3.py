from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, MultiFernet
import base64


def _fernets(data):
    raw_keys = data.draw(
        st.lists(
            st.binary(min_size=32, max_size=32),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    return [Fernet(base64.urlsafe_b64encode(raw_key)) for raw_key in raw_keys]


def _valid_rotation_case(data):
    fernets = _fernets(data)
    plaintext = data.draw(st.binary(min_size=0, max_size=1024))
    timestamp = data.draw(st.integers(min_value=0, max_value=2**31 - 1))
    encrypting_index = data.draw(st.integers(min_value=0, max_value=len(fernets) - 1))

    original_token = fernets[encrypting_index].encrypt_at_time(plaintext, timestamp)
    token_argument = data.draw(st.sampled_from([original_token, original_token.decode("ascii")]))

    return MultiFernet(fernets), fernets, plaintext, timestamp, original_token, token_argument


def _embedded_timestamp(token):
    raw = base64.urlsafe_b64decode(token)
    return int.from_bytes(raw[1:9], "big")


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_returns_bytes_property(data):
    multi_fernet, _, _, _, _, token_argument = _valid_rotation_case(data)

    rotated = multi_fernet.rotate(token_argument)

    assert isinstance(rotated, bytes)


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_preserves_plaintext_property(data):
    multi_fernet, _, plaintext, _, _, token_argument = _valid_rotation_case(data)

    rotated = multi_fernet.rotate(token_argument)

    assert multi_fernet.decrypt(rotated) == plaintext


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_uses_primary_key_property(data):
    _, fernets, plaintext, _, _, token_argument = _valid_rotation_case(data)
    multi_fernet = MultiFernet(fernets)

    rotated = multi_fernet.rotate(token_argument)

    assert fernets[0].decrypt(rotated) == plaintext


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_preserves_timestamp_property(data):
    multi_fernet, _, _, timestamp, original_token, token_argument = _valid_rotation_case(data)

    rotated = multi_fernet.rotate(token_argument)

    assert _embedded_timestamp(original_token) == timestamp
    assert _embedded_timestamp(rotated) == timestamp


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_returns_urlsafe_base64_fernet_token_property(data):
    multi_fernet, _, _, _, _, token_argument = _valid_rotation_case(data)

    rotated = multi_fernet.rotate(token_argument)
    decoded = base64.urlsafe_b64decode(rotated)

    assert set(rotated).issubset(
        set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=")
    )
    assert len(decoded) > 9
    assert decoded[0] == 0x80
    assert multi_fernet.decrypt(rotated)

# End program