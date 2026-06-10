from hypothesis import given, strategies as st, assume
import time
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate (a) valid round-trip tokens (as bytes/str) from random payloads,
# (b) malformed byte/str tokens expected to raise InvalidToken,
# (c) wrong-typed tokens expected to raise TypeError, and (d) expired tokens via
# explicit timestamps to trigger ttl-based InvalidToken. A branch is chosen per example.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    branch = data.draw(st.sampled_from(["valid", "valid_str", "malformed", "wrong_type", "expired"]))

    if branch == "valid":
        # Property 1: round-trip returns original bytes exactly.
        payload = data.draw(st.binary(min_size=0, max_size=2048))
        token = f.encrypt(payload)
        assert f.decrypt(token) == payload

    elif branch == "valid_str":
        # Property 2: a valid token decodes correctly when passed as str.
        payload = data.draw(st.binary(min_size=0, max_size=2048))
        token = f.encrypt(payload)
        token_str = token.decode("ascii")
        assert f.decrypt(token_str) == payload

    elif branch == "malformed":
        # Property 3: malformed/garbage tokens raise InvalidToken.
        garbage = data.draw(
            st.one_of(
                st.binary(min_size=0, max_size=256),
                st.text(max_size=256),
            )
        )
        # Make sure we don't accidentally craft a valid token (astronomically unlikely,
        # but guard against the trivial cases that could collide).
        try:
            f.decrypt(garbage)
            # If it somehow decrypted, it must have been a legitimate token; reject example.
            assume(False)
        except InvalidToken:
            pass  # expected
        except TypeError:
            # garbage was an acceptable type (bytes/str), so TypeError is unexpected here.
            raise AssertionError("Expected InvalidToken, got TypeError for str/bytes input")

    elif branch == "wrong_type":
        # Property 4: non bytes/str tokens raise TypeError.
        bad = data.draw(
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.lists(st.integers(), max_size=5),
                st.none(),
                st.booleans(),
            )
        )
        try:
            f.decrypt(bad)
            raise AssertionError("Expected TypeError for non bytes/str token")
        except TypeError:
            pass  # expected

    else:  # branch == "expired"
        # Property 5: a token older than ttl raises InvalidToken.
        payload = data.draw(st.binary(min_size=0, max_size=256))
        age = data.draw(st.integers(min_value=2, max_value=10_000))
        ttl = data.draw(st.integers(min_value=0, max_value=age - 1))
        created_at = int(time.time()) - age
        token = f.encrypt_at_time(payload, created_at)
        try:
            f.decrypt(token, ttl=ttl)
            raise AssertionError("Expected InvalidToken for expired token")
        except InvalidToken:
            pass  # expected
# End program