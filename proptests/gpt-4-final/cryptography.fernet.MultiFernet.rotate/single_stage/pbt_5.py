from hypothesis import given, example, strategies as st
from cryptography.fernet import Fernet, MultiFernet
from cryptography.fernet import InvalidToken

# Generation of inputs and checking properties
@given(st.lists(elements=st.binary(min_size=32, max_size=32), min_size=1, max_size=5), 
       st.binary(), st.binary(min_size=32, max_size=32))

def test_multi_fernet_rotate(random_keys, random_msg, new_key):
    fernet_instances = [Fernet(key) for key in random_keys]
    f = MultiFernet(fernet_instances)
    token = f.encrypt(random_msg)
    
    # Checking if derived token can be decrypted and matches the original
    decrypted_msg = f.decrypt(token)
    assert decrypted_msg == random_msg, "Decoded Message not matching original"

    # Rotating the token
    rotated_f = MultiFernet([Fernet(new_key)] + fernet_instances)
    rotated_token = rotated_f.rotate(token)
    
    # Checking if the new key can decrypt it
    assert rotated_f.decrypt(rotated_token) == random_msg, "Decoded Message post rotation not matching original"

    # Checking that the old key cannot decrypt it anymore
    try:
        decrypted_msg = f.decrypt(rotated_token)
        assert False, "Old key shouldn't be able to decrypt token post rotation"
    except InvalidToken:
        pass