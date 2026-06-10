from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate valid and invalid Fernet tokens to test decrypt
# - Use st.binary() to generate random byte strings for valid tokens
# - Use Fernet.encrypt() to create valid tokens 
# - Mutate some valid tokens to create invalid ones
# - Generate random ttl values including None and negatives
# - Check that decrypt returns original plaintext for valid tokens
# - Check that decrypt raises InvalidToken for invalid tokens
# - Check that decrypt raises InvalidToken for expired ttl tokens
@given(st.data())
def test_decrypt(data):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    # Generate valid token
    plaintext = data.draw(st.binary())
    token = fernet.encrypt(plaintext)
    
    # Generate invalid token by mutating valid one
    invalid_token = data.draw(st.one_of(
        st.just(token),
        st.builds(bytes, st.binary(min_size=len(token), max_size=len(token)))
    ))
    
    # Generate ttls, including None and negatives
    ttl = data.draw(st.one_of(st.none(), st.integers()))
    
    if invalid_token == token and (ttl is None or ttl >= 0):
        # Should decrypt successfully with original plaintext
        assert fernet.decrypt(token, ttl) == plaintext
    else:
        # Invalid token or ttl should raise exception
        with pytest.raises(InvalidToken):
            fernet.decrypt(invalid_token, ttl)
# End program