from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate a variety of valid and invalid inputs to test decrypt()
# Valid inputs: 
# - Use Fernet.encrypt() to generate valid tokens of random byte strings
# - Optionally specify a ttl as a non-negative int
# Invalid inputs:
# - Generate random strings/bytes that are not valid tokens
# - Generate tokens using a different Fernet key 
# - Use a negative ttl value
# - Pass non-byte/string types as the token
#
# Properties to test:
# - decrypt() returns the original plaintext for valid tokens
# - Raises InvalidToken for invalid tokens or expired ttl 
# - Raises TypeError if passed a non-byte/string token
@given(data=st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    
    # Generate valid token
    plaintext = data.draw(st.binary())
    token = f.encrypt(plaintext)
    ttl = data.draw(st.one_of(st.none(), st.integers(min_value=0)))
    
    # Check valid token decrypts to original plaintext
    assert f.decrypt(token, ttl) == plaintext
    
    # Check invalid token raises InvalidToken
    invalid_token = data.draw(st.one_of(
        st.binary(), 
        st.text(), 
        st.builds(Fernet(Fernet.generate_key()).encrypt, st.binary())
    ))
    with pytest.raises(InvalidToken):
        f.decrypt(invalid_token)
    
    # Check expired ttl raises InvalidToken
    expired_ttl = data.draw(st.integers(max_value=-1))
    with pytest.raises(InvalidToken):  
        f.decrypt(token, expired_ttl)
    
    # Check non-byte/str token raises TypeError
    bad_type_token = data.draw(st.one_of(
        st.integers(), st.floats(), st.lists(st.binary()), st.dictionaries(st.binary(), st.binary())  
    ))
    with pytest.raises(TypeError):
        f.decrypt(bad_type_token)
# End program