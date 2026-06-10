from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(st.binary(min_size=1), st.binary(min_size=1))
def test_encrypt_nonempty_input_returns_nonempty_output(input, key):
    f = Fernet(key)
    encrypted = f.encrypt(input)
    assert encrypted is not None and len(encrypted) > 0

@given(st.binary(min_size=1), st.binary(min_size=1))
def test_decrypt_returns_original_plaintext(input, key):
    f = Fernet(key)
    encrypted = f.encrypt(input)
    decrypted = f.decrypt(encrypted)
    assert decrypted == input

@given(st.binary(min_size=1), st.binary(min_size=1))
def test_encrypt_returns_unique_output(input, key):
    f = Fernet(key)
    encrypted1 = f.encrypt(input)
    encrypted2 = f.encrypt(input)
    assert encrypted1 != encrypted2

@given(st.one_of(st.text(), st.integers(), st.floats()), st.binary(min_size=1))
def test_decrypt_raises_TypeError_with_invalid_token(input, key):
    f = Fernet(key)
    try:
        f.decrypt(input)
    except TypeError:
        assert True
    except Exception:
        assert False

@given(st.binary(min_size=1), st.binary(min_size=1), st.integers(min_value=1))
def test_decrypt_raises_InvalidToken_with_expired_ttl(input, key, ttl):
    f = Fernet(key)
    encrypted = f.encrypt(input)
    try:
        f.decrypt(encrypted, ttl)
        time.sleep(ttl+1)
        f.decrypt(encrypted, ttl)
    except cryptography.fernet.InvalidToken:
        assert True
    except Exception:
        assert False
# End program