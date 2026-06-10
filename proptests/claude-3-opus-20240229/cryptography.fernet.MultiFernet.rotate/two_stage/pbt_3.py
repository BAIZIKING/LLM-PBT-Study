from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate_properties(data):
    # Generate between 2 to 5 Fernet keys
    num_keys = data.draw(st.integers(min_value=2, max_value=5))
    keys = [Fernet(Fernet.generate_key()) for _ in range(num_keys)]
    
    f = MultiFernet(keys)

    # Generate a plaintext message of length 0 to 1000 bytes
    message = data.draw(st.binary(max_size=1000))
    
    token = f.encrypt(message)

    # Property 1: Rotated token can be decrypted with primary key
    f_rotated = MultiFernet([Fernet(Fernet.generate_key())] + keys)
    rotated_token = f_rotated.rotate(token)
    assert f_rotated.decrypt(rotated_token) == message

    # Property 2: Decrypting rotated token gives original plaintext  
    assert f.decrypt(token) == f_rotated.decrypt(rotated_token)

    # Property 3: Rotated token is different from original
    assert rotated_token != token

    # Property 4: InvalidToken raised for invalid tokens
    invalid_token = data.draw(st.binary(max_size=1000))
    try:
        f_rotated.rotate(invalid_token)
        assert False, "Expected InvalidToken exception"
    except InvalidToken:
        pass

    # Property 5: TypeError raised for non-string/bytes input
    non_bytes = data.draw(st.one_of(
        st.integers(), st.floats(), st.text(), 
        st.lists(st.integers()), st.dictionaries(st.text(), st.integers())
    ))
    try:  
        f_rotated.rotate(non_bytes)
        assert False, "Expected TypeError exception"
    except TypeError:
        pass
# End program        