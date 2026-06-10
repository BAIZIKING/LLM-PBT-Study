from hypothesis import given, strategies as st

# Summary: Strategy: draw either arbitrary bytes, including empty bytes, null bytes, high bytes, and larger binary blobs, or many non-bytes such as str, int, float, None, lists, dicts, bytearray, and memoryview. Properties: bytes inputs encrypt to URL-safe base64 bytes tokens that decrypt back to the original data and expose a creation timestamp; non-bytes inputs raise TypeError.
@given(st.data())
def test_cryptography_fernet_Fernet_encrypt(data):
    from cryptography.fernet import Fernet
    import base64
    import time

    input_value = data.draw(
        st.one_of(
            st.binary(min_size=0, max_size=4096),
            st.just(b""),
            st.just(b"\x00"),
            st.just(b"\xff" * 1024),
            st.text(),
            st.integers(),
            st.floats(allow_nan=True, allow_infinity=True),
            st.none(),
            st.booleans(),
            st.lists(st.integers(), max_size=20),
            st.dictionaries(st.text(), st.integers(), max_size=20),
            st.binary(min_size=0, max_size=256).map(bytearray),
            st.binary(min_size=0, max_size=256).map(memoryview),
        ),
        label="data",
    )

    key = base64.urlsafe_b64encode(b"\x00" * 32)
    fernet = Fernet(key)

    if not isinstance(input_value, bytes):
        try:
            fernet.encrypt(input_value)
        except TypeError:
            return
        raise AssertionError("Fernet.encrypt should raise TypeError for non-bytes input")

    before = int(time.time())
    token = fernet.encrypt(input_value)
    after = int(time.time())

    assert isinstance(token, bytes)

    urlsafe_base64_chars = set(
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
    )
    assert set(token) <= urlsafe_base64_chars

    raw_token = base64.urlsafe_b64decode(token)
    assert base64.urlsafe_b64encode(raw_token) == token

    assert fernet.decrypt(token) == input_value

    timestamp = int.from_bytes(raw_token[1:9], "big")
    assert before <= timestamp <= after
# End program