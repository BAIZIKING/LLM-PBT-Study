from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken, MultiFernet

# Summary: This strategy generates a diverse range of inputs for the `rotate` method,
#          including valid and invalid Fernet tokens, as well as edge cases like empty tokens.
@given(st.data())
def test_cryptography_fernet_multifernet_rotate(data):
    # Generate a list of Fernet keys with at least two keys for rotation.
    keys = data.draw(st.lists(st.binary(min_size=32, max_size=32), min_size=2))
    fernets = [Fernet(key) for key in keys]
    multi_fernet = MultiFernet(fernets)

    # Generate a Fernet token using one of the keys.
    token = data.draw(st.sampled_from([f.encrypt(b"test message") for f in fernets]))

    # Test rotation with valid tokens.
    rotated_token = multi_fernet.rotate(token)
    assert multi_fernet.decrypt(rotated_token) == b"test message"

    # Test rotation with invalid tokens (raises InvalidToken).
    invalid_token = data.draw(
        st.one_of(
            st.binary(min_size=1, max_size=len(token) - 1),  # Truncated tokens
            st.binary(min_size=len(token) + 1),  # Extended tokens
            st.text().encode(),  # Non-base64 tokens
        )
    )
    with pytest.raises(InvalidToken):
        multi_fernet.rotate(invalid_token)

    # Test rotation with empty token (raises InvalidToken).
    with pytest.raises(InvalidToken):
        multi_fernet.rotate(b"")

# End program