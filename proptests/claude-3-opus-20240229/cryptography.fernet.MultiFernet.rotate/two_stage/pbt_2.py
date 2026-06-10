from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_output_type(data):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    
    token = data.draw(st.binary(max_size=1024))
    rotated_token = f.rotate(token)
    assert isinstance(rotated_token, bytes)

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_decryptable(data):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key()) 
    f = MultiFernet([key1, key2])
    
    plaintext = data.draw(st.binary(max_size=1024))
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    assert f.decrypt(rotated_token) == plaintext

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_plaintext_match(data):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    
    plaintext = data.draw(st.binary(max_size=1024))  
    token = f.encrypt(plaintext)
    rotated_token = f.rotate(token)
    assert f.decrypt(token) == f.decrypt(rotated_token)

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_invalid_token(data):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    
    invalid_token = data.draw(st.binary(max_size=1024))
    try:
        f.rotate(invalid_token)
    except InvalidToken:
        assert True
    else:
        assert False
        
@given(st.data())        
def test_cryptography_fernet_MultiFernet_rotate_type_error(data):
    key1 = Fernet(Fernet.generate_key())
    key2 = Fernet(Fernet.generate_key())
    f = MultiFernet([key1, key2])
    
    invalid_type = data.draw(st.one_of(st.integers(), st.floats(), st.text()))
    try:
        f.rotate(invalid_type)
    except TypeError:
        assert True
    else:
        assert False
# End program        