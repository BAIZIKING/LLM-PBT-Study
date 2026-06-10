from hypothesis import given, strategies as st

# Summary: Test Fernet decryption with input bytes and ttl as inputs
@given(st.binary(), st.integers(min_value=-1))
def test_fernet_decrypt(input_bytes, ttl):
    from cryptography.fernet import Fernet

    # Generate a key and create Fernet object
    key = Fernet.generate_key()
    f = Fernet(key)

    # encryption
    try:
        token = f.encrypt(input_bytes)
    except TypeError:
        return  # Non bytes input can be disregarded for decrypt test

    # decryption
    try:
        decrypted_text = f.decrypt(token, ttl)
        # If ttl is too small for the token to be valid, a InvalidToken exception should be raised
        assert (ttl is None or ttl >= 0) and decrypted_text == input_bytes
    except Fernet.InvalidToken:
        assert ttl is not None and ttl < 0
# End program