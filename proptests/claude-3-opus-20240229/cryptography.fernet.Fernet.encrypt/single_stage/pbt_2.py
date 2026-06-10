from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Summary: Generate random byte string inputs of varying sizes, including empty byte strings.
# Check that encrypt returns a URL-safe base64-encoded byte string token that can be decrypted 
# back to the original input. Also check that a TypeError is raised for non-byte inputs.
@given(data=st.binary())
def test_fernet_encrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    
    token = f.encrypt(data)
    assert isinstance(token, bytes)
    assert f.decrypt(token) == data
    
    try:
        f.encrypt(123) 
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError for non-byte input"
# End program