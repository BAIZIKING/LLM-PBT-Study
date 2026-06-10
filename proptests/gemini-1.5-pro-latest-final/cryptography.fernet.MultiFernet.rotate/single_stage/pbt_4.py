from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: This strategy generates a variety of inputs for the `rotate` method, including:
# - Valid Fernet tokens encrypted with different keys.
# - Invalid Fernet tokens (malformed, wrong padding, etc.).
# - Non-bytes/str inputs to check for TypeError.

@given(st.data())
def test_cryptography_fernet_multifernet_rotate(data):
    # Generate multiple Fernet keys for MultiFernet instances
    num_keys = data.draw(st.integers(min_value=2, max_value=5))
    keys = [Fernet(Fernet.generate_key()) for _ in range(num_keys)]

    # Create MultiFernet instances with different key combinations
    multifernet1 = MultiFernet(keys)
    # Create a second MultiFernet with a different primary key for rotation
    keys.insert(0, Fernet(Fernet.generate_key()))  
    multifernet2 = MultiFernet(keys)

    # Generate valid and invalid tokens
    valid_token = data.draw(st.binary(min_size=1))  # Any binary data
    encrypted_token = multifernet1.encrypt(valid_token)
    invalid_token = data.draw(
        st.one_of(
            st.text(),  # Wrong format (not bytes)
            st.binary(max_size=15),  # Too short to be valid
            st.just(b"not a valid token"),
        )
    )

    # Test cases:

    # 1. Valid token rotation:
    try:
        rotated_token = multifernet2.rotate(encrypted_token)
        # Check if the rotated token can be decrypted using the new primary key
        decrypted_data = multifernet2.decrypt(rotated_token)
        assert decrypted_data == valid_token
    except InvalidToken:
        # This should not happen for a valid token
        assert False

    # 2. Invalid token raises InvalidToken exception:
    with pytest.raises(InvalidToken):
        multifernet2.rotate(invalid_token)

    # 3. Non-bytes/str input raises TypeError:
    with pytest.raises(TypeError):
        multifernet2.rotate(123)  # Example non-string/bytes input