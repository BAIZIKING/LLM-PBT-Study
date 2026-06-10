from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Summary: 
# Generate random byte strings of varying lengths to test a wide range of inputs.
# Use fernet.encrypt() to encrypt the data and check key properties:
# 1) The encrypted token is a byte string
# 2) The encrypted token is different than the original plaintext 
# 3) The token can be decrypted back to the original plaintext
# 4) Decrypting an invalid token raises an exception
@given(st.binary())
def test_cryptography_fernet_encrypt(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    token = fernet.encrypt(data)
    assert isinstance(token, bytes) # Check token is bytes
    assert token != data # Check token is different than plaintext
    assert fernet.decrypt(token) == data # Check token decrypts to original data
    
    invalid_key = Fernet.generate_key()
    invalid_fernet = Fernet(invalid_key)
    try:
        invalid_fernet.decrypt(token)
        assert False # Should not reach here
    except:
        pass # Expected exception on decrypting with wrong key
        
# End program