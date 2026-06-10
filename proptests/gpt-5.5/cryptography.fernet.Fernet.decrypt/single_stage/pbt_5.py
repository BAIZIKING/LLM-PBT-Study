from hypothesis import given, strategies as st

# Summary: Generate one random scenario per example: valid fresh tokens, valid old tokens
# without ttl, expired old tokens with ttl, tampered tokens with invalid signatures,
# malformed base64 Fernet-like tokens, and non-bytes/non-str token values. Plaintexts,
# token representation bytes-vs-str, ttl values, malformed payloads, and invalid Python
# object types are randomized to cover normal use and edge cases.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    import base64
    from cryptography.fernet import Fernet, InvalidToken

    key = base64.urlsafe_b64encode(b"\x00" * 32)
    f = Fernet(key)

    scenario = data.draw(
        st.sampled_from(
            [
                "valid_fresh_token",
                "valid_old_token_without_ttl",
                "expired_token_with_ttl",
                "tampered_token",
                "malformed_token",
                "non_bytes_or_str_token",
            ]
        ),
        label="scenario",
    )

    plaintext = data.draw(st.binary(max_size=256), label="plaintext")
    token_as_str = data.draw(st.booleans(), label="token_as_str")

    def maybe_str(token):
        return token.decode("ascii") if token_as_str else token

    def assert_raises_invalid_token(fn):
        try:
            fn()
        except InvalidToken:
            return
        assert False, "Expected cryptography.fernet.InvalidToken"

    if scenario == "valid_fresh_token":
        token = maybe_str(f.encrypt(plaintext))
        ttl = data.draw(
            st.one_of(st.none(), st.integers(min_value=10**8, max_value=2**31 - 1)),
            label="ttl",
        )

        decrypted = f.decrypt(token, ttl=ttl)

        # Property: a valid Fernet token decrypts to the original plaintext bytes.
        assert decrypted == plaintext
        assert isinstance(decrypted, bytes)

    elif scenario == "valid_old_token_without_ttl":
        token = maybe_str(f.encrypt_at_time(plaintext, current_time=0))

        decrypted = f.decrypt(token, ttl=None)

        # Property: when ttl is None, token age is not considered.
        assert decrypted == plaintext
        assert isinstance(decrypted, bytes)

    elif scenario == "expired_token_with_ttl":
        token = maybe_str(f.encrypt_at_time(plaintext, current_time=0))
        ttl = data.draw(st.integers(min_value=0, max_value=10**6), label="ttl")

        # Property: a token older than ttl seconds is invalid.
        assert_raises_invalid_token(lambda: f.decrypt(token, ttl=ttl))

    elif scenario == "tampered_token":
        token = f.encrypt(plaintext)
        decoded = bytearray(base64.urlsafe_b64decode(token))
        decoded[-1] ^= 1
        tampered_token = maybe_str(base64.urlsafe_b64encode(bytes(decoded)))

        # Property: a token with an invalid signature is rejected.
        assert_raises_invalid_token(lambda: f.decrypt(tampered_token))

    elif scenario == "malformed_token":
        payload = data.draw(st.binary(max_size=128), label="malformed_payload")
        malformed_token = maybe_str(base64.urlsafe_b64encode(b"\x00" + payload))

        # Property: malformed Fernet tokens are rejected.
        assert_raises_invalid_token(lambda: f.decrypt(malformed_token))

    else:
        non_token = data.draw(
            st.one_of(
                st.none(),
                st.integers(),
                st.floats(allow_nan=True, allow_infinity=True),
                st.lists(st.integers(), max_size=5),
                st.dictionaries(st.text(max_size=5), st.integers(), max_size=5),
            ),
            label="non_bytes_or_str_token",
        )

        # Property: token values that are not bytes or str raise TypeError.
        try:
            f.decrypt(non_token)
        except TypeError:
            return
        assert False, "Expected TypeError for non-bytes/non-str token"

# End program