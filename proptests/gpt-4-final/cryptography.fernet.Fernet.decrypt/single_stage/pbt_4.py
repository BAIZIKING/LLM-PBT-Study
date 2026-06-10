from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Key used for encryption and decryption. Generated using Fernet.generate_key()
key = Fernet.generate_key()
f = Fernet(key)

@given(st.binary(min_size=1), st.one_of(st.integers(min_value=0, max_value=1000), st.none()))
def test_cryptography_fernet_decrypt(token, ttl):
    try:
        result = f.decrypt(token, ttl)
        # If decryption succeeds, the result should be bytes.
        assert isinstance(result, bytes)
    except (InvalidToken, TypeError) as e:
        # It should raise either InvalidToken or TypeError only.
        pass
    except Exception as e:
        # If it raises any other exception, the test should fail.
        assert False, f"Unexpected exception raised: {e}"
# End program