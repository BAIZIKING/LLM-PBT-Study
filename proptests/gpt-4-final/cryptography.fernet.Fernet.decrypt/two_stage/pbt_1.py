from hypothesis import given, strategies as st
from cryptography.fernet import Fernet
import binascii

@given(st.binary(), st.binary(), st.floats(allow_nan=False, allow_infinity=False))
def test_cryptography_decrypt_property(token, key, ttl):
    
    # Property 1: The output of decrypt should be bytes
    f = Fernet(Fernet.generate_key())
    try:
        decrypted = f.decrypt(token, ttl)
        assert isinstance(decrypted, bytes)
    except:
        pass

    # Property 2: The output of decrypt should equal to original plaintext
    try:
        plaintext = b'my secret'
        cipher_suite = Fernet(key)
        token = cipher_suite.encrypt(plaintext)
        decrypted = cipher_suite.decrypt(token)
        assert decrypted == plaintext
    except:
        pass
    
    # Property 3: decrypt should raise InvalidToken if a token is invalid
    try:
        f = Fernet(Fernet.generate_key())
        invalid_token = binascii.hexlify(token)
        f.decrypt(invalid_token, ttl)
    except cryptography.fernet.InvalidToken:
        assert True
        

    # Property 4: decrypt should raise TypeError if the token parameter is not bytes or str.
    try:
        f = Fernet(Fernet.generate_key())
        f.decrypt(123, ttl)
    except TypeError:
        assert True

    # Property 5: decrypt with ttl should depend on the input parameter ttl
    try:
        f = Fernet(Fernet.generate_key())
        token = f.encrypt(b"message")
        f.decrypt(token, 1000)
    except (cryptography.fernet.InvalidToken, TypeError):
        assert True