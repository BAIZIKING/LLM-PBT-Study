from hypothesis import given, strategies as st
from cryptography.fernet import Fernet, InvalidToken

# Summary: Generate valid Fernet tokens from random plaintext bytes, both as bytes and str; generate expired valid tokens with varied ttl values; generate malformed byte/string tokens; and generate non-bytes/non-str tokens. Check that valid tokens decrypt to the original plaintext, expired/malformed/wrong-key tokens raise InvalidToken, and unsupported token types raise TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    other_key = b"AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE="
    f = Fernet(key)
    other_f = Fernet(other_key)

    case = data.draw(
        st.sampled_from(
            [
                "valid_bytes",
                "valid_str",
                "expired",
                "malformed_bytes",
                "malformed_str",
                "wrong_type",
                "wrong_key",
            ]
        )
    )

    plaintext = data.draw(st.binary(min_size=0, max_size=1024))

    if case == "valid_bytes":
        token = f.encrypt(plaintext)
        ttl = data.draw(st.one_of(st.none(), st.integers(min_value=3600, max_value=10**9)))
        assert f.decrypt(token, ttl=ttl) == plaintext

    elif case == "valid_str":
        token = f.encrypt(plaintext).decode("ascii")
        ttl = data.draw(st.one_of(st.none(), st.integers(min_value=3600, max_value=10**9)))
        assert f.decrypt(token, ttl=ttl) == plaintext

    elif case == "expired":
        token = f.encrypt_at_time(plaintext, current_time=0)
        ttl = data.draw(st.integers(min_value=0, max_value=10**6))
        try:
            f.decrypt(token, ttl=ttl)
            assert False, "expired token should raise InvalidToken"
        except InvalidToken:
            pass

    elif case == "malformed_bytes":
        token = data.draw(st.binary(min_size=0, max_size=256))
        ttl = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=10**6)))
        try:
            f.decrypt(token, ttl=ttl)
            assert False, "malformed bytes token should raise InvalidToken"
        except InvalidToken:
            pass

    elif case == "malformed_str":
        token = data.draw(st.text(min_size=0, max_size=256))
        ttl = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=10**6)))
        try:
            f.decrypt(token, ttl=ttl)
            assert False, "malformed str token should raise InvalidToken"
        except InvalidToken:
            pass

    elif case == "wrong_type":
        token = data.draw(
            st.one_of(
                st.none(),
                st.integers(),
                st.floats(allow_nan=False),
                st.lists(st.integers(), max_size=10),
                st.dictionaries(st.text(max_size=5), st.integers(), max_size=5),
            )
        )
        try:
            f.decrypt(token)
            assert False, "non-bytes/non-str token should raise TypeError"
        except TypeError:
            pass

    elif case == "wrong_key":
        token = other_f.encrypt(plaintext)
        try:
            f.decrypt(token)
            assert False, "token signed with a different key should raise InvalidToken"
        except InvalidToken:
            pass
# End program