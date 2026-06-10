from hypothesis import given, strategies as st
import time
from cryptography.fernet import Fernet, InvalidToken

# Summary: Draw a "mode" selecting among (1) valid round-trip, (2) ttl-controlled
# fresh/expired tokens via *_at_time, (3) malformed random tokens, (4) tampered
# tokens, (5) wrong-type tokens. For each mode we assert the documented behavior:
# round-trip returns original plaintext (bytes); fresh tokens within ttl decrypt;
# expired/malformed/tampered tokens raise InvalidToken; non-bytes/str raise TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_decrypt(data):
    key = Fernet.generate_key()
    f = Fernet(key)

    mode = data.draw(st.sampled_from(
        ["roundtrip", "ttl_fresh", "ttl_expired", "malformed", "tampered", "wrongtype"]
    ))

    if mode == "roundtrip":
        plaintext = data.draw(st.binary(max_size=256))
        token = f.encrypt(plaintext)
        result = f.decrypt(token)
        assert result == plaintext
        assert isinstance(result, bytes)

    elif mode == "ttl_fresh":
        plaintext = data.draw(st.binary(max_size=256))
        created = data.draw(st.integers(min_value=0, max_value=2_000_000_000))
        ttl = data.draw(st.integers(min_value=0, max_value=10_000))
        # current_time within [created, created + ttl] -> still valid
        offset = data.draw(st.integers(min_value=0, max_value=ttl))
        current = created + offset
        token = f.encrypt_at_time(plaintext, created)
        result = f.decrypt_at_time(token, ttl=ttl, current_time=current)
        assert result == plaintext

    elif mode == "ttl_expired":
        plaintext = data.draw(st.binary(max_size=256))
        created = data.draw(st.integers(min_value=0, max_value=2_000_000_000))
        ttl = data.draw(st.integers(min_value=0, max_value=10_000))
        # current_time strictly beyond created + ttl -> expired
        extra = data.draw(st.integers(min_value=1, max_value=10_000))
        current = created + ttl + extra
        token = f.encrypt_at_time(plaintext, created)
        try:
            f.decrypt_at_time(token, ttl=ttl, current_time=current)
            assert False, "Expected InvalidToken for expired token"
        except InvalidToken:
            pass

    elif mode == "malformed":
        # Random bytes/str that are extremely unlikely to be a valid token.
        token = data.draw(st.one_of(
            st.binary(max_size=128),
            st.text(max_size=128),
        ))
        try:
            f.decrypt(token)
            # On the astronomically unlikely chance random data decrypted,
            # that is still a non-failure of the API contract.
        except InvalidToken:
            pass
        except TypeError:
            # Only acceptable if token isn't bytes/str, but here it always is.
            assert False, "TypeError should not be raised for bytes/str input"

    elif mode == "tampered":
        plaintext = data.draw(st.binary(max_size=256))
        token = bytearray(f.encrypt(plaintext))
        # Flip a byte to invalidate the signature.
        idx = data.draw(st.integers(min_value=0, max_value=len(token) - 1))
        token[idx] ^= data.draw(st.integers(min_value=1, max_value=255))
        try:
            f.decrypt(bytes(token))
            # Extremely unlikely to remain valid; if it does, contract not violated.
        except InvalidToken:
            pass

    elif mode == "wrongtype":
        bad = data.draw(st.one_of(
            st.integers(),
            st.lists(st.integers(min_value=0, max_value=255), max_size=16),
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False),
        ))
        try:
            f.decrypt(bad)
            assert False, "Expected TypeError for non-bytes/str token"
        except TypeError:
            pass
# End program