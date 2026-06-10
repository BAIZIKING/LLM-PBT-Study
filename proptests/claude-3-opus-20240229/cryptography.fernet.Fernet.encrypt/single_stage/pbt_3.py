from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: 
# - Generate random byte strings of various lengths for the data parameter
# - Check that encrypt returns a byte string Fernet token
# - Check that the original data can be decrypted from the token 
# - Check that modifying the token raises an InvalidToken exception on decrypt
@given(data=st.binary())
def test_cryptography_fernet_Fernet_encrypt(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    token = fernet.encrypt(data)
    assert isinstance(token, bytes)
    
    decrypted_data = fernet.decrypt(token)
    assert data == decrypted_data
    
    modified_token = bytearray(token)
    modified_token[0] = modified_token[0] ^ 1  # Flip one bit
    modified_token = bytes(modified_token)
    
    try:
        fernet.decrypt(modified_token)
        assert False, "Expected InvalidToken exception"
    except InvalidToken:
        pass
# End program        