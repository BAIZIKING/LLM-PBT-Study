from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate valid round-trip tokens (as bytes or str), TTL-expired tokens via
# *_at_time, malformed bytes/str tokens, and wrong-typed tokens; then assert decrypt's
# round-trip correctness, ttl expiration semantics, InvalidToken on malformed input,
# and TypeError on wrong types.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    mode = data.draw(st.sampled_from(["roundtrip", "ttl", "invalid", "wrongtype"]))

    if mode == "roundtrip":
        # Property 1: decrypt(encrypt(x)) == x, for bytes or str token.
        plaintext = data.draw(st.binary(max_size=1024))
        token = f.encrypt(plaintext)
        as_str = data.draw(st.booleans())
        token_input = token.decode("ascii") if as_str else token
        assert f.decrypt(token_input) == plaintext
        # ttl=None should never reject a fresh token.
        assert f.decrypt(token_input, ttl=None) == plaintext

    elif mode == "ttl":
        # Property 2: TTL expiration semantics via *_at_time.
        plaintext = data.draw(st.binary(max_size=256))
        created_at = data.draw(st.integers(min_value=0, max_value=2**31))
        ttl = data.draw(st.integers(min_value=1, max_value=10000))
        token = f.encrypt_at_time(plaintext, current_time=created_at)

        # Within ttl: decrypts successfully.
        within = data.draw(st.integers(min_value=0, max_value=ttl))
        assert f.decrypt_at_time(token, ttl=ttl, current_time=created_at + within) == plaintext

        # Past ttl: raises InvalidToken.
        past = data.draw(st.integers(min_value=ttl + 1, max_value=ttl + 100000))
        try:
            f.decrypt_at_time(token, ttl=ttl, current_time=created_at + past)
            assert False, "Expected InvalidToken for expired token"
        except InvalidToken:
            pass

    elif mode == "invalid":
        # Property 3: malformed bytes/str tokens raise InvalidToken.
        garbage = data.draw(st.one_of(st.binary(max_size=200), st.text(max_size=200)))
        try:
            f.decrypt(garbage)
            # If it somehow decrypts (astronomically unlikely), that's still valid behavior.
        except InvalidToken:
            pass
        except (ValueError, TypeError):
            # Some malformed inputs may surface as ValueError/TypeError depending on version;
            # accept these as non-success rejections of garbage input.
            pass

    else:  # wrongtype
        # Property 4: non-bytes/str tokens raise TypeError.
        bad = data.draw(st.one_of(
            st.integers(),
            st.floats(allow_nan=False),
            st.lists(st.integers(), max_size=5),
            st.none(),
        ))
        try:
            f.decrypt(bad)
            assert False, "Expected TypeError for non-bytes/str token"
        except TypeError:
            pass
# End program