from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: Generate random lists of Fernet keys and messages (as bytes or str).
# Use the generated keys to create a MultiFernet. Encrypt the message with the 
# MultiFernet, then generate a new random list of keys and create a second 
# MultiFernet. Call rotate() on the second MultiFernet with the encrypted token.
# Check that the rotated token can be decrypted by the second MultiFernet, the
# decrypted plaintext matches the original message, and that InvalidToken is  
# raised if passing an invalid token to rotate(). Also check that TypeError is
# raised if msg is not bytes or str.
@given(
    keys=st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=5), 
    msg=st.one_of(st.binary(), st.text()),
    invalid_token=st.one_of(st.binary(), st.text()),
    non_str_bytes=st.one_of(
        st.lists(st.integers()), st.dictionaries(st.text(), st.text()))
)
def test_cryptography_fernet_multifernet_rotate(keys, msg, invalid_token, non_str_bytes):
    key_objects = [Fernet(key) for key in keys]
    f = MultiFernet(key_objects)
    
    token = f.encrypt(msg)
    
    new_keys = keys + [Fernet.generate_key()]  
    f2 = MultiFernet([Fernet(key) for key in new_keys])
    
    rotated = f2.rotate(token)
    decrypted = f2.decrypt(rotated)
    
    assert isinstance(rotated, bytes)
    assert decrypted == msg
    
    try:
        f2.rotate(invalid_token)
    except InvalidToken:
        pass
    else:
        raise AssertionError("InvalidToken not raised")
        
    try:
        f2.rotate(non_str_bytes)
    except TypeError:
        pass        
    else:
        raise AssertionError("TypeError not raised for non-bytes/str input")
# End program        