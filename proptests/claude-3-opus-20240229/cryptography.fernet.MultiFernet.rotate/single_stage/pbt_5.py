from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: 
# Generate random byte strings for the token message
# Generate 1 to 5 random Fernet keys
# Randomly select one of the keys to encrypt the message 
# Create a MultiFernet with a random ordering of the keys
# Check that:
#   rotate returns a byte string
#   the rotated token can be decrypted with the MultiFernet
#   an InvalidToken error is raised if the token is modified
#   a TypeError is raised if the input is not bytes or str
@given(
    msg=st.binary(min_size=1), 
    keys=st.lists(st.builds(Fernet.generate_key), min_size=1, max_size=5),
    data=st.data()
)
def test_cryptography_fernet_MultiFernet_rotate(msg, keys, data):
    encrypt_key = data.draw(st.sampled_from(keys))
    f = Fernet(encrypt_key)
    token = f.encrypt(msg)

    mf = MultiFernet(keys)
    rotated = mf.rotate(token)
    
    assert isinstance(rotated, bytes)
    assert mf.decrypt(rotated) == msg

    bad_token = bytes(b ^ 0x01 for b in token)
    try:
        mf.rotate(bad_token)
        assert False, "Expected InvalidToken"
    except InvalidToken:
        pass

    try:
        mf.rotate(123)
        assert False, "Expected TypeError"
    except TypeError:
        pass
# End program