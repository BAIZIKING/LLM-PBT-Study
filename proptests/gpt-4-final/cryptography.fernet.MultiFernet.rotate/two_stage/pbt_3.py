from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

@given(st.binary(), st.lists(st.binary(min_size=32, max_size=32), min_size=1, unique=True))
def test_rotate_property(message, keys):
    # Create MultiFernet instances
    fernets = [Fernet(key) for key in keys]
    f1 = MultiFernet(fernets)
    
    # Encrypt the message
    token = f1.encrypt(message)
    
    # Create new MultiFernet instance with extra key for rotation
    new_key = Fernet.generate_key()
    fernets.insert(0, Fernet(new_key)) # add new key to front
    f2 = MultiFernet(fernets)
    
    # Rotate the token
    rotated = f2.rotate(token)
    
    # Decrypt post rotation
    decrypted = f2.decrypt(rotated)
    
    # Validate type of rotated token
    assert isinstance(rotated, bytes)
    
    # Validate successful rotation
    assert decrypted == message
    
    # Validate decryption consistency
    assert f1.decrypt(token) == f2.decrypt(rotated)
    
    # Exception testing
    with pytest.raises(TypeError):
        f2.rotate(int(tokens)) 
        
    with pytest.raises(cryptography.exceptions.InvalidToken):
        f2.rotate(b'invalid_token')
        
# End program