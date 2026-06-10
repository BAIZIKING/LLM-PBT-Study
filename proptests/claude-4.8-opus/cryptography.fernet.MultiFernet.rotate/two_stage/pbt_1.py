from hypothesis import given, strategies as st
import pytest
from cryptography.fernet import Fernet, MultiFernet, InvalidToken
import base64
import struct


# Strategy to generate a list of distinct Fernet keys (1 to 5 keys)
def fernet_keys():
    return st.lists(
        st.builds(lambda _: Fernet.generate_key(), st.integers()),
        min_size=1,
        max_size=5,
    )


@given(st.data())
def test_rotate_returns_bytes():
    """Property 1: The rotated token is always of type bytes."""
    data = st.data()

    @given(keys=fernet_keys(), message=st.binary(max_size=1024))
    def inner(keys, message):
        mf = MultiFernet([Fernet(k) for k in keys])
        token = mf.encrypt(message)
        rotated = mf.rotate(token)
        assert isinstance(rotated, bytes)

    inner()
# End program


@given(st.data())
def test_rotate_preserves_plaintext():
    """Property 2: Decrypting the rotated token yields the same plaintext."""

    @given(keys=fernet_keys(), message=st.binary(max_size=1024))
    def inner(keys, message):
        mf = MultiFernet([Fernet(k) for k in keys])
        token = mf.encrypt(message)
        rotated = mf.rotate(token)
        assert mf.decrypt(rotated) == message

    inner()
# End program


@given(st.data())
def test_rotate_preserves_timestamp():
    """Property 3: The rotated token preserves the original timestamp."""

    def extract_timestamp(fernet, token):
        # Decode the URL-safe base64 token and extract the timestamp.
        decoded = base64.urlsafe_b64decode(token)
        # Format: version (1 byte) | timestamp (8 bytes) | ...
        (ts,) = struct.unpack(">Q", decoded[1:9])
        return ts

    @given(keys=fernet_keys(), message=st.binary(max_size=1024))
    def inner(keys, message):
        fernets = [Fernet(k) for k in keys]
        mf = MultiFernet(fernets)
        token = mf.encrypt(message)
        rotated = mf.rotate(token)
        orig_ts = extract_timestamp(fernets[0], token)
        rotated_ts = extract_timestamp(fernets[0], rotated)
        assert orig_ts == rotated_ts

    inner()
# End program


@given(st.data())
def test_rotate_uses_primary_key():
    """Property 4: The rotated token decrypts under the primary (first) key."""

    @given(keys=fernet_keys(), message=st.binary(max_size=1024))
    def inner(keys, message):
        fernets = [Fernet(k) for k in keys]
        mf = MultiFernet(fernets)
        token = mf.encrypt(message)
        rotated = mf.rotate(token)
        # The primary key alone should be able to decrypt the rotated token.
        primary = fernets[0]
        assert primary.decrypt(rotated) == message

    inner()
# End program


@given(st.data())
def test_rotate_invalid_inputs():
    """Property 5: Non-bytes/str msg raises TypeError; invalid token raises InvalidToken."""

    @given(
        keys=fernet_keys(),
        bad_type=st.one_of(
            st.integers(),
            st.floats(),
            st.none(),
            st.lists(st.integers(), max_size=5),
            st.dictionaries(st.text(max_size=3), st.integers(), max_size=3),
        ),
        bad_token=st.binary(min_size=1, max_size=128),
    )
    def inner(keys, bad_type, bad_token):
        mf = MultiFernet([Fernet(k) for k in keys])

        # Non bytes/str input must raise TypeError.
        with pytest.raises(TypeError):
            mf.rotate(bad_type)

        # A random/garbage bytes token must raise InvalidToken.
        with pytest.raises(InvalidToken):
            mf.rotate(bad_token)

    inner()
# End program