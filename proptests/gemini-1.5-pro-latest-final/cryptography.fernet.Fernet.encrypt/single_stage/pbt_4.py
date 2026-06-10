from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Summary: The generation strategy aims to create a diverse range of input data for the `encrypt` function, including:
# - Random byte strings of varying lengths to cover different data sizes.
# - Byte strings containing special characters and non-ASCII characters to test encoding robustness.
# - Empty byte strings to handle edge cases.
@given(st.data())
def test_cryptography_fernet_encrypt(data):
    # Generate a random Fernet key.
    key = Fernet.generate_key()
    f = Fernet(key)

    # Draw a random byte string as input data.
    input_data = data.draw(st.binary())

    # Encrypt the data.
    encrypted_data = f.encrypt(input_data)

    # Assertions based on API documentation:
    # - Check that the encrypted data is a byte string.
    assert isinstance(encrypted_data, bytes)

    # - Check that the encrypted data is not the same as the input data.
    assert encrypted_data != input_data

    # - Check that the encrypted data can be decrypted back to the original input data.
    decrypted_data = f.decrypt(encrypted_data)
    assert decrypted_data == input_data
# End program