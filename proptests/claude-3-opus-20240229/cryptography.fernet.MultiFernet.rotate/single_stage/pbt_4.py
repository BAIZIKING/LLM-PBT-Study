from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Generate a variety of inputs by:
# - Creating multiple Fernet keys to initialize MultiFernet with 
# - Generating byte string messages of different lengths
# - Sometimes generating invalid tokens by corrupting valid ones
# This exercises key rotation with multiple keys, messages of 
# different sizes, and invalid input tokens.
@given(
    st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=5),
    st.binary(min_size=0, max_size=1000), 
    st.booleans()
)
def test_multifernet_rotate(keys, message, invalidate_token):
    fernet = MultiFernet([Fernet(key) for key in keys])
    token = fernet.encrypt(message)

    if invalidate_token:
        token = token[:-1] 

    if invalidate_token:
        # Property: Rotating an invalid token should raise InvalidToken
        try:
            rotated = fernet.rotate(token)
            assert False, "Expected InvalidToken"
        except InvalidToken:
            pass
    else:
        # Property: Rotating a valid token should succeed and the rotated
        # token should decrypt to the original message
        rotated = fernet.rotate(token)
        assert fernet.decrypt(rotated) == message
        
        # Property: Rotating a token should change it (due to re-encryption) 
        assert rotated != token
# End program