from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: Generate a mix of valid and invalid inputs to test rotate()
# - Build random lists of 1-10 Fernet keys to initialize MultiFernet instances 
# - Generate valid tokens by encrypting random byte strings
# - Also generate random invalid byte strings and unicode strings
# - Check that rotate returns the rotated token for valid inputs
# - Check that InvalidToken or TypeError is raised for invalid inputs
@given(
    keys=st.lists(st.binary(min_size=32, max_size=32), min_size=1, max_size=10),
    msg=st.one_of(
        st.binary(min_size=1, max_size=1024), 
        st.binary(min_size=200, max_size=300),
        st.text()
    )
)
def test_multifernet_rotate(keys, msg):
    fernet_keys = [Fernet(key) for key in keys]
    mf = MultiFernet(fernet_keys)
    
    if isinstance(msg, bytes):
        try:
            token = mf.encrypt(msg)
            rotated = mf.rotate(token)
            assert mf.decrypt(rotated) == msg
        except InvalidToken:
            pass
    else:
        try:
            mf.rotate(msg)
            assert False, "Expected TypeError"
        except TypeError:
            pass
# End program