from cryptography.fernet import Fernet, MultiFernet
from hypothesis import given, strategies as st

@given(st.data())
def test_multi_fernet_rotate(data):
    f = MultiFernet([Fernet(Fernet.generate_key()), Fernet(Fernet.generate_key())])
    
    msg = data.draw(st.one_of(st.binary(), st.text()))
    try:
        # If msg is not valid fernet token, this will throw InvalidToken exception
        rotated = f.rotate(msg)
        # If rotate function succeeds, the result should be bytes.
        assert isinstance(rotated, bytes)
    except cryptography.fernet.InvalidToken:
        # If msg was not a valid token, the function should throw InvalidToken exception
        pass
    except TypeError:
        # If msg is not string or bytes, this should throw TypeError
        assert not isinstance(msg, (bytes, str))