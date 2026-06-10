from hypothesis import given, strategies as st
import base64
import time

import pytest
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate valid Fernet tokens from random plaintext, bytes/str token forms,
# unexpired and expired ttl values, guaranteed-invalid base64 Fernet-shaped tokens,
# tokens authenticated with the wrong key, and non-bytes/non-str token inputs.
# Check that authentic unexpired tokens decrypt to the original plaintext, ttl=None
# ignores token age, expired/invalid/wrong-key tokens raise InvalidToken, and invalid
# token types raise TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    f = Fernet(Fernet.generate_key())
    plaintext = data.draw(st.binary(max_size=2048))
    case = data.draw(
        st.sampled_from(
            [
                "valid_without_ttl",
                "valid_with_ttl",
                "expired_with_ttl",
                "wrong_key",
                "invalid_token_bytes_or_str",
                "wrong_token_type",
            ]
        )
    )

    if case == "valid_without_ttl":
        now = int(time.time())
        created_at = data.draw(st.integers(min_value=0, max_value=now))
        token = f.encrypt_at_time(plaintext, created_at)

        token_input = token.decode("ascii") if data.draw(st.booleans()) else token

        assert f.decrypt(token_input) == plaintext

    elif case == "valid_with_ttl":
        now = int(time.time())
        age = data.draw(st.integers(min_value=0, max_value=100_000))
        ttl = age + data.draw(st.integers(min_value=3_600, max_value=1_000_000))
        token = f.encrypt_at_time(plaintext, now - age)

        token_input = token.decode("ascii") if data.draw(st.booleans()) else token

        assert f.decrypt(token_input, ttl=ttl) == plaintext

    elif case == "expired_with_ttl":
        now = int(time.time())
        ttl = data.draw(st.integers(min_value=0, max_value=1_000_000))
        extra_age = data.draw(st.integers(min_value=120, max_value=10_000))
        token = f.encrypt_at_time(plaintext, now - ttl - extra_age)

        token_input = token.decode("ascii") if data.draw(st.booleans()) else token

        with pytest.raises(InvalidToken):
            f.decrypt(token_input, ttl=ttl)

    elif case == "wrong_key":
        token = f.encrypt(plaintext)
        token_input = token.decode("ascii") if data.draw(st.booleans()) else token
        other_f = Fernet(Fernet.generate_key())

        with pytest.raises(InvalidToken):
            other_f.decrypt(token_input)

    elif case == "invalid_token_bytes_or_str":
        invalid_payload = data.draw(st.binary(max_size=256))
        invalid_token = base64.urlsafe_b64encode(b"\x00" + invalid_payload)
        token_input = (
            invalid_token.decode("ascii") if data.draw(st.booleans()) else invalid_token
        )

        with pytest.raises(InvalidToken):
            f.decrypt(token_input)

    else:
        bad_token = data.draw(
            st.one_of(
                st.none(),
                st.integers(),
                st.floats(allow_nan=True, allow_infinity=True),
                st.lists(st.integers(), max_size=5),
                st.dictionaries(st.text(max_size=5), st.integers(), max_size=5),
            )
        )

        with pytest.raises(TypeError):
            f.decrypt(bad_token)
# End program