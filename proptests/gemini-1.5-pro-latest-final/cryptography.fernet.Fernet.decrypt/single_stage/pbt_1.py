from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: The generation strategy aims to create a diverse set of inputs for Fernet.decrypt, including:
# - Valid Fernet tokens generated using Fernet.encrypt with varying data.
# - Invalid tokens with different types of modifications (e.g., altered ciphertext, timestamp, or signature).
# - Edge cases such as empty tokens, tokens with invalid base64 encoding, and tokens exceeding the maximum length.

@given(st.data())
def test_fernet_decrypt(data):
    # Generate a valid Fernet key.
    key = Fernet.generate_key()
    f = Fernet(key)

    # Strategy 1: Generate valid tokens with varying data and timestamps.
    plaintext = data.draw(st.binary())
    current_time = data.draw(st.integers())
    valid_token = f.encrypt_at_time(plaintext, current_time)

    # Property 1: Decrypting a valid token should return the original plaintext.
    decrypted_data = f.decrypt_at_time(valid_token, ttl=None, current_time=current_time)
    assert decrypted_data == plaintext

    # Strategy 2: Generate invalid tokens with different modifications.
    invalid_tokens = data.draw(
        st.one_of(
            # Tamper with the ciphertext.
            st.binary(min_size=len(valid_token)).map(lambda x: x[: len(valid_token)]),
            # Modify the timestamp.
            st.binary(min_size=len(valid_token)).map(lambda x: valid_token[:10] + x[10:]),
            # Corrupt the signature.
            st.binary(min_size=len(valid_token)).map(lambda x: x[:-20] + valid_token[-20:]),
        )
    )

    # Property 2: Decrypting an invalid token should raise an InvalidToken exception.
    for invalid_token in invalid_tokens:
        with pytest.raises(InvalidToken):
            f.decrypt(invalid_token)

    # Strategy 3: Test edge cases (e.g., empty token, invalid base64).
    edge_cases = ["", "invalid_base64", "a" * 10000]  # Exceeding max token length

    # Property 3: Decrypting edge cases should raise an InvalidToken exception.
    for edge_case in edge_cases:
        with pytest.raises(InvalidToken):
            f.decrypt(edge_case)
# End program