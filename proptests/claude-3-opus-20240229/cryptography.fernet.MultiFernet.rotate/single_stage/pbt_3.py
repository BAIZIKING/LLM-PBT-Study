from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: 
# Generate lists of 1-5 Fernet keys. For each key list, instantiate a MultiFernet.
# Generate byte string messages of various lengths. 
# Encrypt the message with the MultiFernet to get a token.
# Rotate the token and verify:
# 1) The rotated token can be decrypted successfully 
# 2) Decrypting the rotated token gives the original message
# 3) Rotating an invalid token raises an InvalidToken exception
# 4) Passing a non-bytes/str value raises a TypeError
@given(keys=st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=5),
       message=st.binary(min_size=0, max_size=1000),
       invalid_token=st.one_of(st.binary(), st.text()),
       not_bytes_str=st.one_of(st.integers(), st.dates()))
def test_multifernet_rotate(keys, message, invalid_token, not_bytes_str):
    key_objs = [Fernet(key) for key in keys]
    mf = MultiFernet(key_objs)

    token = mf.encrypt(message)
    rotated = mf.rotate(token)
    assert mf.decrypt(rotated) == message

    try:
        mf.rotate(invalid_token)
    except InvalidToken:
        pass
    else:
        raise AssertionError("Rotating an invalid token should raise InvalidToken")
        
    try:
        mf.rotate(not_bytes_str)  
    except TypeError:
        pass
    else:
        raise AssertionError("Rotating a non-bytes/str value should raise TypeError")
# End program