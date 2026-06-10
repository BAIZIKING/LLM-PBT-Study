from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

@given(st.binary())
def test_rotate(msg):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    
    # Assume token was previously encrypted by MultiFernet instance
    token = f.encrypt(msg)
    
    # Create a new MultiFernet instance with a new key
    key3 = Fernet(Fernet.generate_key())
    f2 = MultiFernet([key3, key1, key2])
    
    # Ensure rotation doesn't raise exceptions unexpectedly
    try:
        rotated_token = f2.rotate(token)
    except (TypeError, InvalidToken):
        raise AssertionError("Exception raised during token rotation")
    
    # Ensure rotated token can be decrypted and equals original message
    assert f2.decrypt(rotated_token) == msg

# End Program