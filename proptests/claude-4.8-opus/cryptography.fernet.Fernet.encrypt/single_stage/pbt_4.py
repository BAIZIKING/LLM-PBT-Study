from hypothesis import given, strategies as st

# Summary: Generate arbitrary byte strings (including empty, single-byte, and large
# binary payloads) using st.binary(). For each, create a fresh Fernet key, encrypt the
# data, and verify: (1) the token is bytes, (2) the token is valid URL-safe base64,
# and (3) decrypting the token returns the original data (round-trip correctness).
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt():
    import base64
    from cryptography.fernet import Fernet

    data_strategy = st.binary(min_size=0, max_size=4096)

    @given(data_strategy)
    def inner(data):
        f = Fernet(Fernet.generate_key())
        token = f.encrypt(data)

        # Property 2: encrypt returns bytes
        assert isinstance(token, bytes)

        # Property 3: token is valid URL-safe base64 (decodes without error)
        # urlsafe_b64decode will raise if the token is not valid base64.
        base64.urlsafe_b64decode(token)

        # Property 1: round-trip correctness
        assert f.decrypt(token) == data

    inner()
# End program