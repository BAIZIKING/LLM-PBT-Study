from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: This test generates random bytestrings to simulate potential tokens and ensures that
# the rotate function either successfully rotates the token or raises the appropriate exception. 
# It covers cases with valid and invalid tokens, including empty strings and strings with 
# incorrect padding.

@given(st.binary())
def test_cryptography_fernet_multifernet_rotate(token):
    # Create a MultiFernet instance with at least two keys
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f = MultiFernet([key1, key2])

    try:
        # Attempt to rotate the token
        rotated_token = f.rotate(token)

        # Check if the rotated token can be decrypted with the first key
        decrypted_data = f.decrypt(rotated_token)

        # Assert that the decrypted data matches the original token
        assert decrypted_data == token
    except InvalidToken:
        # If the token is invalid, ensure it can't be decrypted by any key
        for key in f._fernets:
            with pytest.raises(InvalidToken):
                key.decrypt(token)
# End program