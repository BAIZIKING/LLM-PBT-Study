from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Generating random bytes for encryption and integer for ttl
@given(input_bytes=st.binary(), ttl=st.integers(min_value=-100, max_value=100))
def test_fernet_decrypt(input_bytes, ttl):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(input_bytes)
    
    try:
        result = f.decrypt(token, ttl)
        assert result == input_bytes
    except Exception:
        assert ttl <= 0