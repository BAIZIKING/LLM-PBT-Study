from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Define a strategy for generating Fernet keys
keys = st.binary(min_size=32, max_size=32)

# 1. Decrypted data matches original data
@given(st.binary(), keys)
def test_fernet_roundtrip(data, key):
    f = Fernet(key)
    encrypted = f.encrypt(data)
    decrypted = f.decrypt(encrypted)
    assert data == decrypted

# 2. Tampering with ciphertext raises an exception
@given(st.binary(), keys)
def test_fernet_tampering(data, key):
    f = Fernet(key)
    token = f.encrypt(data)
    # Tamper with the token
    tampered_token = bytearray(token)
    tampered_token[0] ^= 0xFF
    with pytest.raises(cryptography.fernet.InvalidToken):
        f.decrypt(tampered_token)

# 3. Different keys produce different ciphertexts
@given(st.binary(), keys, keys)
def test_fernet_different_keys(data, key1, key2):
    assume(key1 != key2)
    f1 = Fernet(key1)
    f2 = Fernet(key2)
    token1 = f1.encrypt(data)
    token2 = f2.encrypt(data)
    assert token1 != token2

# 4. Ciphertext length depends on plaintext length
@given(st.binary())
def test_fernet_ciphertext_length(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(data)
    # Overhead is consistent for Fernet tokens
    assert len(token) == len(data) + 44

# 5. Time-based encryption/decryption consistency
@given(st.binary(), st.integers(), st.integers())
def test_fernet_time_based(data, time1, time2):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt_at_time(data, time1)
    # Successful decryption with matching time
    decrypted = f.decrypt_at_time(token, ttl=None, current_time=time1)
    assert decrypted == data
    # Exception with mismatched time
    assume(time1 != time2)
    with pytest.raises(cryptography.fernet.InvalidToken):
        f.decrypt_at_time(token, ttl=None, current_time=time2)
# End program