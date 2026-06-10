from hypothesis import given, strategies as st, assume
import time
import pytest
from cryptography.fernet import Fernet, InvalidToken


# Property 1: The output of decrypt is always of type bytes.
@given(data=st.binary(max_size=1024))
def test_cryptography_fernet_Fernet_decrypt_output_is_bytes(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    result = f.decrypt(token)
    assert isinstance(result, bytes)
# End program


# Property 2: Decrypting a token produced by encrypt returns the original plaintext.
@given(data=st.binary(max_size=1024))
def test_cryptography_fernet_Fernet_decrypt_roundtrip(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    result = f.decrypt(token)
    assert result == data
# End program


# Property 3: A token older than ttl raises InvalidToken.
@given(
    data=st.binary(max_size=1024),
    age=st.integers(min_value=1, max_value=10**6),
    ttl=st.integers(min_value=0, max_value=10**6),
)
def test_cryptography_fernet_Fernet_decrypt_expired_raises(data, age, ttl):
    assume(age > ttl)
    key = Fernet.generate_key()
    f = Fernet(key)
    now = int(time.time())
    creation_time = now - age
    token = f.encrypt_at_time(data, creation_time)
    with pytest.raises(InvalidToken):
        f.decrypt_at_time(token, ttl, now)
# End program


# Property 4: A tampered/malformed token raises InvalidToken.
@given(
    data=st.binary(max_size=1024),
    flip_index=st.integers(min_value=0, max_value=10**4),
)
def test_cryptography_fernet_Fernet_decrypt_tampered_raises(data, flip_index):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = bytearray(f.encrypt(data))
    idx = flip_index % len(token)
    # Flip a byte to a different value, ensuring the token changes.
    token[idx] = token[idx] ^ 0x01
    tampered = bytes(token)
    assume(tampered != bytes(f.encrypt(data)))  # extremely unlikely collision
    with pytest.raises(InvalidToken):
        f.decrypt(tampered)
# End program


# Property 5: A non-bytes/str token raises TypeError.
@given(
    bad_token=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.lists(st.integers()),
        st.dictionaries(st.text(), st.integers()),
        st.none(),
    )
)
def test_cryptography_fernet_Fernet_decrypt_bad_type_raises(bad_token):
    key = Fernet.generate_key()
    f = Fernet(key)
    with pytest.raises(TypeError):
        f.decrypt(bad_token)
# End program