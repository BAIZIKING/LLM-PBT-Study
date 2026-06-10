from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import base64

# Define a strategy for generating Fernet keys
keys = st.builds(Fernet.generate_key)

# Define a strategy for generating binary data
data = st.binary(max_size=1024)  # Limit data size to avoid potential overflows

@given(keys, data)
def test_decrypt_matches_original(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert decrypted == data

@given(keys, data)
def test_token_length_deterministic(key, data):
    f = Fernet(key)
    token1 = f.encrypt(data)
    token2 = f.encrypt(data)
    assert len(token1) == len(token2)

@given(keys, data)
def test_token_is_urlsafe_base64(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    try:
        base64.urlsafe_b64decode(token)
        is_valid_base64 = True
    except Exception:
        is_valid_base64 = False
    assert is_valid_base64

@given(data, st.sampled_from(keys.example()))
def test_different_keys_different_tokens(data, keys):
    token1 = Fernet(keys[0]).encrypt(data)
    token2 = Fernet(keys[1]).encrypt(data)
    assert token1 != token2

@given(keys, data)
def test_tampering_detection(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    tampered_token = bytearray(token)
    tampered_token[0] ^= 0x01  # Flip a bit
    with pytest.raises(cryptography.fernet.InvalidToken):
        f.decrypt(tampered_token)
# End program