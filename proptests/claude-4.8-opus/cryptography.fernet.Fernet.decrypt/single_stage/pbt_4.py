from hypothesis import given, strategies as st
import pytest
from cryptography.fernet import Fernet, InvalidToken

# Summary: We generate a fresh Fernet key per example, then exercise decrypt across
# four scenarios chosen by hypothesis: (1) valid bytes/str tokens for round-trip and
# TTL-expiration checks using encrypt_at_time/decrypt_at_time, (2) malformed
# bytes/str tokens expecting InvalidToken, and (3) non-bytes/str tokens expecting
# TypeError. Plaintext, ttl values, and timing offsets are drawn from broad ranges
# including empty payloads and negative/zero/large ttls.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    scenario = data.draw(st.sampled_from(["valid", "malformed", "wrong_type"]))

    if scenario == "valid":
        plaintext = data.draw(st.binary(min_size=0, max_size=256))
        as_str = data.draw(st.booleans())

        # Property 1 & 2: round-trip correctness for bytes and str tokens (ttl=None).
        token = f.encrypt(plaintext)
        token_input = token.decode("ascii") if as_str else token
        assert f.decrypt(token_input, ttl=None) == plaintext

        # Property 3: TTL expiration semantics via *_at_time.
        created_time = data.draw(st.integers(min_value=0, max_value=2_000_000_000))
        ttl = data.draw(st.integers(min_value=0, max_value=10_000))
        offset = data.draw(st.integers(min_value=-100, max_value=20_000))
        current_time = created_time + offset

        timed_token = f.encrypt_at_time(plaintext, created_time)
        age = current_time - created_time

        if 0 <= age <= ttl:
            # Within ttl and not from the "future" -> must decrypt back correctly.
            assert f.decrypt_at_time(timed_token, ttl, current_time) == plaintext
        elif age > ttl:
            # Older than ttl -> InvalidToken.
            with pytest.raises(InvalidToken):
                f.decrypt_at_time(timed_token, ttl, current_time)
        # (age < 0 means a future-dated token; behavior is unconstrained here.)

    elif scenario == "malformed":
        # Property 4: random non-token bytes/str must raise InvalidToken.
        bad = data.draw(st.one_of(
            st.binary(min_size=0, max_size=128),
            st.text(min_size=0, max_size=128),
        ))
        ttl = data.draw(st.one_of(st.none(), st.integers(min_value=-10, max_value=10_000)))
        # Skip the astronomically unlikely case of generating a genuinely valid token.
        try:
            f.decrypt(bad, ttl=ttl)
            valid = True
        except InvalidToken:
            valid = False
        assert valid is False

    else:  # wrong_type
        # Property 5: non-bytes/str tokens must raise TypeError.
        bad = data.draw(st.one_of(
            st.integers(),
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.lists(st.integers(), max_size=5),
        ))
        with pytest.raises(TypeError):
            f.decrypt(bad)
# End program