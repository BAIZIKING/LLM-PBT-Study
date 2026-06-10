from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

# Generation strategy:
# - Generate random byte strings of varying lengths from 0 to 1000 bytes 
#   to test different size inputs
# - Include empty byte string to test 0-length edge case
# - Include non-byte types like integers, strings, None to check TypeError is raised
@given(st.one_of(
    st.binary(max_size=1000),  
    st.just(b''), 
    st.integers(), 
    st.text(), 
    st.none()
))
def test_fernet_encrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    # If data is bytes, encrypt should return bytes
    if isinstance(data, bytes):
        encrypted = f.encrypt(data)
        assert isinstance(encrypted, bytes)

        # Decrypting the encrypted token should round-trip back to original data 
        decrypted = f.decrypt(encrypted)
        assert decrypted == data
    else:
        # encrypt should raise TypeError if data is not bytes
        try:
            f.encrypt(data)
            assert False, "Expected TypeError"
        except TypeError:
            pass
# End program