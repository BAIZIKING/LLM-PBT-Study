from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet

# Property 1: Type Consistency
@given(msg=st.binary())
def test_type_consistency(msg):
    f = MultiFernet([Fernet(Fernet.generate_key())])
    rotated_msg = f.rotate(msg)
    assert isinstance(rotated_msg, bytes), "rotated output should be bytes"

# Property 2: Consistent Decryption
@given(msg=st.text())
def test_consistent_decryption(msg):
    f = MultiFernet([Fernet(Fernet.generate_key())])
    token = f.encrypt(msg.encode())
    rotated_token = f.rotate(token)
    assert f.decrypt(token) == f.decrypt(rotated_token), "decryption should be consistent after rotation"

# Property 3: InvalidToken Exception
@given(st.binary(), st.data())
def test_invalid_token_exception(corrupted_token, fernet_instance):
    fernet_instance.draw(Fernet(Fernet.generate_key()))
    try:
        fernet_instance.rotate(corrupted_token)
    except cryptography.fernet.InvalidToken:
        pass   # correct behavior for invalid tokens

# Property 4: URL-safe base64-encoded
@given(msg=st.text())
def test_url_safe_base64_encoded_result(msg):
    f = MultiFernet([Fernet(Fernet.generate_key())])
    rotated_token = f.rotate(f.encrypt(msg.encode()))
    assert rotated_token == rotated_token.urlsafe_b64encode(rotated_token), "output should be url-safe base64-encoded"

# Property 5: Preservation of Timestamp
@given(msg=st.text())
def test_preservation_of_timestamp(msg):  
    f = MultiFernet([Fernet(Fernet.generate_key())])
    token = f.encrypt(msg.encode())
    rotated_token = f.rotate(token)
    assert f.extract_timestamp(token) == f.extract_timestamp(rotated_token), "timestamp should be preserved after rotation"
# End program