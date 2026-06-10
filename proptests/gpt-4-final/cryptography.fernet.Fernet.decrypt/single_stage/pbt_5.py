from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(token = st.binary(), ttl = st.one_of(st.none(), st.integers(min_value = 0)))
def test_cryptography_fernet_decrypt(token, ttl):
    key = Fernet.generate_key()
    f = Fernet(key)
    test_token = f.encrypt(token)
    result = f.decrypt(test_token, ttl)
    assert isinstance(result, bytes)
    assert result == token

    with pytest.raises(cryptography.fernet.InvalidToken):
        f.decrypt(b"invalid token", ttl)

    with pytest.raises(TypeError):
        f.decrypt(None, ttl)

# End program