from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

@given(st.binary(min_size=44, max_size=44), st.binary(min_size=1))
def test_multi_fernet_rotate(key, msg):
    f = MultiFernet([Fernet(key)])
    token = f.encrypt(msg)

    # Test rotation with the initial key
    rotated =  f.rotate(token)
    assert f.decrypt(rotated) == msg

    # Test rotation with a new key
    new_key = Fernet(Fernet.generate_key())
    f2 = MultiFernet([new_key, Fernet(key)])
    rotated = f2.rotate(token)
    assert f2.decrypt(rotated) == msg

    # Test rotation failure with a totally new set of keys
    f3 = MultiFernet([Fernet(Fernet.generate_key())])
    try:
        rotated = f3.rotate(token)
    except Exception as e:
        assert isinstance(e, (cryptography.fernet.InvalidToken))