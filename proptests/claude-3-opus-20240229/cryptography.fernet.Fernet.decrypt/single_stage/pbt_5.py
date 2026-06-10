from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate a random Fernet key and message. Encrypt the message to get a token.
# Feed the token into decrypt, sometimes modifying it to be invalid.
# Check that decrypt returns the original message for valid tokens, and raises
# an InvalidToken exception for invalid tokens.
@given(
    key=st.binary(min_size=32, max_size=32),  
    message=st.binary(min_size=0, max_size=1024),
    modify_token=st.booleans(),
    invalid_token=st.booleans(),
    ttl=st.one_of(st.none(), st.integers(min_value=0))
)
def test_cryptography_fernet_decrypt(key, message, modify_token, invalid_token, ttl):
    f = Fernet(key)
    token = f.encrypt(message)
    
    if modify_token:
        token = token[:-1] 
    if invalid_token:
        token = token + b'1'
    
    if not modify_token and not invalid_token:
        assert f.decrypt(token, ttl) == message
    else:
        with pytest.raises(InvalidToken):
            f.decrypt(token, ttl)
# End program