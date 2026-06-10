from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: Generates various Fernet keys, valid and invalid tokens, and MultiFernet instances to test rotate.
@given(st.data())
def test_cryptography_fernet_multifernet_rotate(data):
    # Generate keys and MultiFernet instances
    keys = data.draw(st.lists(st.binary(), min_size=2, max_size=5))
    f1 = MultiFernet(keys[:-1])  # MultiFernet without the last key
    f2 = MultiFernet(keys)      # MultiFernet with all keys (for rotation)

    # Generate valid and invalid tokens
    valid_token = data.draw(st.builds(f1.encrypt, st.binary()))
    invalid_token_bytes = data.draw(st.binary())
    corrupted_token = bytearray(valid_token)
    corrupted_token[0] ^= 0xFF  # Flip a bit to corrupt the token

    # Test valid token rotation
    rotated_token = f2.rotate(valid_token)
    assert f2.decrypt(rotated_token) == f1.decrypt(valid_token)

    # Test invalid token handling
    with pytest.raises(InvalidToken):
        f2.rotate(invalid_token_bytes)
    with pytest.raises(InvalidToken):
        f2.rotate(corrupted_token)

    # Test type check
    with pytest.raises(TypeError):
        f2.rotate(123)  # Pass an integer
# End program