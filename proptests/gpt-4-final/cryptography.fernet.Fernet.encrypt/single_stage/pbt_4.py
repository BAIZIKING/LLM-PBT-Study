from hypothesis import given, strategies as st
from cryptography.fernet import Fernet

@given(st.binary())
def test_Fernet_encrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    # Check that an exception is thrown when input data is not bytes
    if not isinstance(data, bytes):
        with pytest.raises(TypeError):
            f.encrypt(data)
        return

    # Check that the function outputs bytes (Fernet Token)
    token = f.encrypt(data)
    assert isinstance(token, bytes)

    # Make sure the encryption can be decrypted to return the original data
    original_data = f.decrypt(token)
    assert original_data == data
# End program