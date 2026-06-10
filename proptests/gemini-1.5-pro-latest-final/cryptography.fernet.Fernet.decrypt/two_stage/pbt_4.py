from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken
import time

# Define strategies for key generation and data
key_strategy = st.binary(min_size=32, max_size=32)  # 32-byte key
data_strategy = st.binary(max_size=1024)  # Limit data size for performance

# Property 1: Output length equality
@given(key_strategy, data_strategy)
def test_decrypt_length(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    assert len(decrypted) == len(data)

# Property 2: Idempotence
@given(key_strategy, data_strategy)
def test_decrypt_idempotence(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    decrypted = f.decrypt(token)
    double_decrypted = f.decrypt(decrypted)
    assert decrypted == double_decrypted

# Property 3: Determinism
@given(key_strategy, data_strategy)
def test_decrypt_determinism(key, data):
    f1 = Fernet(key)
    f2 = Fernet(key)
    token = f1.encrypt(data)
    decrypted1 = f1.decrypt(token)
    decrypted2 = f2.decrypt(token)
    assert decrypted1 == decrypted2

# Property 4: Tamper evidence
@given(key_strategy, data_strategy)
def test_decrypt_tamper_evidence(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    tampered_token = bytearray(token)
    tampered_token[0] ^= 0x01  # Modify a byte
    with pytest.raises(InvalidToken):
        f.decrypt(tampered_token)

# Property 5: Time-bound decryption
@given(key_strategy, data_strategy, st.integers(min_value=1, max_value=3600))
def test_decrypt_ttl(key, data, ttl):
    f = Fernet(key)
    current_time = int(time.time())
    token = f.encrypt_at_time(data, current_time)
    # Decrypt with ttl should work
    f.decrypt_at_time(token, ttl, current_time) 
    # Decrypt with expired ttl should fail
    with pytest.raises(InvalidToken):
        f.decrypt_at_time(token, ttl, current_time + ttl + 1) 
# End program