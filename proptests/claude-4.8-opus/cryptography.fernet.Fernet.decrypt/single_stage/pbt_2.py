from hypothesis import given, strategies as st
import pytest
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate diverse inputs for Fernet.decrypt by (1) round-tripping random
# bytes plaintext as bytes/str tokens, (2) feeding malformed tokens and wrong-key
# tokens to force InvalidToken, (3) exercising ttl expiration via decrypt_at_time
# with controlled timestamps, and (4) passing wrong-typed tokens to force TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    mode = data.draw(st.sampled_from(
        ["roundtrip", "roundtrip_str", "malformed", "wrong_key", "ttl", "wrong_type"]
    ))

    if mode == "roundtrip":
        # Property: decrypt(encrypt(x)) == x (token as bytes)
        plaintext = data.draw(st.binary(max_size=512))
        token = f.encrypt(plaintext)
        assert f.decrypt(token) == plaintext

    elif mode == "roundtrip_str":
        # Property: decrypt also accepts str tokens and round-trips correctly
        plaintext = data.draw(st.binary(max_size=512))
        token = f.encrypt(plaintext)
        token_str = token.decode("ascii")
        assert f.decrypt(token_str) == plaintext

    elif mode == "malformed":
        # Property: malformed (non-token) input raises InvalidToken
        bad_token = data.draw(st.one_of(
            st.binary(max_size=128),
            st.text(max_size=128),
        ))
        # A genuinely valid token is astronomically unlikely from random data.
        with pytest.raises(InvalidToken):
            f.decrypt(bad_token)

    elif mode == "wrong_key":
        # Property: a token signed with a different key fails verification
        plaintext = data.draw(st.binary(max_size=256))
        token = f.encrypt(plaintext)
        other = Fernet(Fernet.generate_key())
        with pytest.raises(InvalidToken):
            other.decrypt(token)

    elif mode == "ttl":
        # Property: tokens older than ttl raise InvalidToken; within ttl they decrypt.
        plaintext = data.draw(st.binary(max_size=256))
        t0 = data.draw(st.integers(min_value=0, max_value=2_000_000_000))
        ttl = data.draw(st.integers(min_value=0, max_value=10_000))
        token = f.encrypt_at_time(plaintext, t0)

        # Within the validity window -> decrypts correctly.
        assert f.decrypt_at_time(token, ttl, t0) == plaintext

        # Strictly past the window -> InvalidToken.
        with pytest.raises(InvalidToken):
            f.decrypt_at_time(token, ttl, t0 + ttl + 1)

    else:  # wrong_type
        # Property: non-bytes/str token raises TypeError
        bad = data.draw(st.one_of(
            st.integers(),
            st.lists(st.integers(), max_size=5),
            st.none(),
        ))
        with pytest.raises(TypeError):
            f.decrypt(bad)
# End program