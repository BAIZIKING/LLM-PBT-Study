from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Summary: The generation strategy aims to create a diverse set of inputs for the 'encrypt' function, 
# including both typical and edge cases. It generates random byte sequences of varying lengths, 
# covering empty sequences, short sequences, and longer sequences. 

@given(st.binary(min_size=0, max_size=1024))
def test_fernet_encrypt(data):
    # Generate a random Fernet key
    key = Fernet.generate_key()
    f = Fernet(key)

    # Test encryption and decryption roundtrip
    encrypted_data = f.encrypt(data)
    decrypted_data = f.decrypt(encrypted_data)

    # Property 1: Decrypted data should match the original input
    assert data == decrypted_data

    # Property 2: Encrypted data should be different from the original input
    assert data != encrypted_data

    # Property 3: Encryption should be deterministic (same input, same key, same output)
    encrypted_data_again = f.encrypt(data)
    assert encrypted_data == encrypted_data_again
# End program