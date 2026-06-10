from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(st.binary())
def test_fernet_encrypt(input_data):
    # Generate a key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Encrypt the data
    token = f.encrypt(input_data)
    
    # Ensure the encrypted token can be decrypted to original message
    assert f.decrypt(token) == input_data

    # Ensure encryption is deterministic for same key and input
    assert f.encrypt(input_data) == token
# End program