from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(st.bytes(), st.data())
def test_fernet_encrypt(plaintext, data):
    key = Fernet.generate_key()  # Generate a key
    f = Fernet(key)  # Create Fernet object
    
    # Property1: If the input is not of type bytes, TypeError should be risen
    if not isinstance(plaintext, bytes):
        with pytest.raises(TypeError):
            f.encrypt(plaintext)
        return
        
    # Now we know plaintext is bytes, let's encrypt it
    ciphertext = f.encrypt(plaintext)
    
    # Property2: The output of encrypt should not be the same as the input
    assert ciphertext != plaintext, "Ciphertext is same as the plaintext"

    # Property3: Given the same plaintext, we should get the same ciphertext
    same_ciphertext = f.encrypt(plaintext)
    assert ciphertext == same_ciphertext, "Ciphertext is different for same plaintext"
    
# End program