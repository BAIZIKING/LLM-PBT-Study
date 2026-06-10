from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: 
# Generate valid Fernet keys using fernet_keys()
# Generate valid Fernet tokens by encrypting random byte strings
# Generate invalid tokens by fuzzing/mutating valid tokens
# Generate random TTL integers, including None and negative values
# Check that decrypt() returns original plaintext for valid tokens
# Check that decrypt() raises InvalidToken for invalid tokens
# Check TTL expiration by comparing current time to token timestamp
@given(key=st.sampled_from(st.fernet_keys()), 
       data=st.binary(min_size=0, max_size=1024),
       token=st.one_of(st.fernet_tokens(), st.fernet_tokens().map(lambda t: t[:-1]+bytes([t[-1]^1]))),
       ttl=st.one_of(st.none(), st.integers()))
def test_cryptography_fernet_decrypt(key, data, token, ttl):
    f = Fernet(key)
    
    if token in f._encrypt_from_parts(data, int(time.time())):
        # Valid token
        assert f.decrypt(token, ttl) == data
        
        # TTL expiration
        current_time = int(time.time()) 
        token_time = f.extract_timestamp(token)
        if ttl is not None and current_time - token_time > ttl:
            with pytest.raises(InvalidToken):
                f.decrypt(token, ttl)

    else:
        # Invalid token
        with pytest.raises(InvalidToken):
            f.decrypt(token, ttl)
# End program