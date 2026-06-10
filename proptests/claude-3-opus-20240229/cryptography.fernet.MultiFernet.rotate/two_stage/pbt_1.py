from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property1(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    
    plaintext = data.draw(st.binary(max_size=1024))
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    
    assert f.decrypt(rotated_token) == plaintext

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property2(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    key3 = Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    
    plaintext = data.draw(st.binary(max_size=1024))
    token = Fernet(key3).encrypt(plaintext)
    
    try:
        f.rotate(token)
        assert False, "Expected InvalidToken exception"
    except InvalidToken:
        pass

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property3(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    
    invalid_token = data.draw(st.binary(max_size=1024))
    
    try:
        f.rotate(invalid_token)
        assert False, "Expected InvalidToken exception"
    except InvalidToken:
        pass

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property4(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    
    invalid_type = data.draw(st.one_of(
        st.integers(),
        st.floats(),
        st.lists(st.binary()),
        st.dictionaries(st.binary(), st.binary())
    ))
    
    try:
        f.rotate(invalid_type)
        assert False, "Expected TypeError"
    except TypeError:
        pass

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_property5(data):
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    f = MultiFernet([Fernet(key1), Fernet(key2)])
    
    plaintext = data.draw(st.binary(max_size=1024))
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    
    assert set(rotated_token.decode('utf-8')) <= set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
# End program