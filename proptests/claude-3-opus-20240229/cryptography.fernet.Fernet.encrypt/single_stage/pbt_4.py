from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Strategy:
# - Generate random Fernet keys using Fernet.generate_key()
# - Generate byte string data of various lengths, including empty string 
# - Lengths from 0 up to a max size like 1MB
# - Use byte strings with random bytes, not just ASCII text
# - Encrypt the data and check properties of the token

@given(key=st.builds(Fernet.generate_key), data=st.binary(max_size=1024*1024))
def test_fernet_encrypt(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    
    # Check that token is a byte string
    assert isinstance(token, bytes)
    
    # Check that token is not equal to original data
    assert token != data
    
    # Check that token is URL-safe base64 encoded
    # i.e. no +, /, or = characters
    assert b'+' not in token
    assert b'/' not in token
    assert b'=' not in token
    
    # Check that decrypting token returns original data 
    decrypted = f.decrypt(token)
    assert decrypted == data
# End program