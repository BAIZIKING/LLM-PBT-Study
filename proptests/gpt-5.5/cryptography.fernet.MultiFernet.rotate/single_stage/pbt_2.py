from hypothesis import given, strategies as st
import base64

from cryptography.fernet import Fernet, MultiFernet, InvalidToken

# Summary: Generate MultiFernet instances from random 32-byte keys, then generate one of:
# valid Fernet tokens encrypted by any configured key as bytes or ASCII str, invalid Fernet-like
# base64 tokens with a guaranteed wrong version byte as bytes or ASCII str, or non-bytes/non-str
# values. For valid tokens, check rotation returns bytes, preserves plaintext, uses the primary key,
# and preserves the original timestamp. For invalid tokens, check InvalidToken. For wrong types,
# check TypeError.
@given(st.data())
def test_cryptography_fernet_MultiFernet_rotate(data):
    key_materials = data.draw(
        st.lists(
            st.binary(min_size=32, max_size=32),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    fernets = [
        Fernet(base64.urlsafe_b64encode(key_material))
        for key_material in key_materials
    ]
    multi = MultiFernet(fernets)

    case = data.draw(st.sampled_from(["valid", "invalid", "wrong_type"]))

    if case == "valid":
        plaintext = data.draw(st.binary(max_size=4096))
        timestamp = data.draw(st.integers(min_value=0, max_value=2**32))
        encrypting_key_index = data.draw(
            st.integers(min_value=0, max_value=len(fernets) - 1)
        )

        token = fernets[encrypting_key_index].encrypt_at_time(
            plaintext,
            timestamp,
        )
        msg = token.decode("ascii") if data.draw(st.booleans()) else token

        rotated = multi.rotate(msg)

        assert isinstance(rotated, bytes)
        assert multi.decrypt(rotated) == plaintext
        assert fernets[0].decrypt(rotated) == plaintext
        assert fernets[0].extract_timestamp(rotated) == timestamp

    elif case == "invalid":
        first_byte = data.draw(
            st.one_of(
                st.integers(min_value=0, max_value=0x7F),
                st.integers(min_value=0x81, max_value=0xFF),
            )
        )
        rest = data.draw(st.binary(max_size=256))
        invalid_token = base64.urlsafe_b64encode(bytes([first_byte]) + rest)
        msg = invalid_token.decode("ascii") if data.draw(st.booleans()) else invalid_token

        try:
            multi.rotate(msg)
        except InvalidToken:
            pass
        else:
            raise AssertionError("rotate() accepted an invalid Fernet token")

    else:
        msg = data.draw(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=True, allow_infinity=True),
                st.lists(st.integers(), max_size=5),
                st.dictionaries(st.text(max_size=5), st.integers(), max_size=5),
            )
        )

        try:
            multi.rotate(msg)
        except TypeError:
            pass
        else:
            raise AssertionError("rotate() accepted a non-bytes/non-str msg")
# End program