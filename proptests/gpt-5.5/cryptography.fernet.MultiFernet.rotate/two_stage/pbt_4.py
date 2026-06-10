from hypothesis import given, strategies as st
import cryptography
from cryptography.fernet import Fernet, MultiFernet
import base64


def _draw_valid_rotation_case(data):
    raw_keys = data.draw(
        st.lists(
            st.binary(min_size=32, max_size=32),
            min_size=2,
            max_size=5,
            unique=True,
        ),
        label="raw_keys",
    )
    fernets = [Fernet(base64.urlsafe_b64encode(raw_key)) for raw_key in raw_keys]

    plaintext = data.draw(st.binary(min_size=0, max_size=2048), label="plaintext")
    token_key_index = data.draw(
        st.integers(min_value=0, max_value=len(fernets) - 1),
        label="token_key_index",
    )

    token = fernets[token_key_index].encrypt(plaintext)
    multi_fernet = MultiFernet(fernets)

    return multi_fernet, fernets, token_key_index, plaintext, token


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_returns_bytes_property(data):
    multi_fernet, _, _, _, token = _draw_valid_rotation_case(data)

    rotated = multi_fernet.rotate(token)

    assert isinstance(rotated, bytes)


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_preserves_plaintext_property(data):
    multi_fernet, _, _, plaintext, token = _draw_valid_rotation_case(data)

    rotated = multi_fernet.rotate(token)

    assert multi_fernet.decrypt(rotated) == plaintext


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_preserves_timestamp_property(data):
    multi_fernet, fernets, token_key_index, _, token = _draw_valid_rotation_case(data)

    rotated = multi_fernet.rotate(token)

    original_timestamp = fernets[token_key_index].extract_timestamp(token)
    rotated_timestamp = fernets[0].extract_timestamp(rotated)

    assert rotated_timestamp == original_timestamp


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_uses_primary_key_property(data):
    multi_fernet, fernets, _, plaintext, token = _draw_valid_rotation_case(data)

    rotated = multi_fernet.rotate(token)

    assert fernets[0].decrypt(rotated) == plaintext


@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_returns_urlsafe_base64_fernet_token_property(data):
    multi_fernet, _, _, _, token = _draw_valid_rotation_case(data)

    rotated = multi_fernet.rotate(token)

    urlsafe_base64_alphabet = set(
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
    )
    decoded = base64.urlsafe_b64decode(rotated)

    assert all(byte in urlsafe_base64_alphabet for byte in rotated)
    assert base64.urlsafe_b64encode(decoded) == rotated
    assert decoded[0] == 0x80


# End program