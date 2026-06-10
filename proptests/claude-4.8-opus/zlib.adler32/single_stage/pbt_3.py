from hypothesis import given, strategies as st
import zlib

# Summary: Generate random byte strings (including empty) for `data`, and for the
# optional `value` parameter generate either None (test default) or a wide range of
# integers (0, 1, near/above 2**32) to cover masking/edge cases. A second byte string
# is also generated to verify the running/concatenation checksum property.
@given(st.data())
def test_zlib_adler32():
    data = st.data
    # Draw the primary inputs
    d = data.draw(st.binary(min_size=0, max_size=512))
    value = data.draw(st.none() | st.integers(min_value=0, max_value=2**34))
    d2 = data.draw(st.binary(min_size=0, max_size=512))

    # Compute checksum with or without the optional value
    if value is None:
        result = zlib.adler32(d)
        default_result = zlib.adler32(d, 1)
        # Property 3: default starting value is 1
        assert result == default_result
    else:
        result = zlib.adler32(d, value)

    # Property 1: result is an unsigned 32-bit integer
    assert 0 <= result <= 2**32 - 1
    # Property 2: result is an int
    assert isinstance(result, int)

    # Property 4: running checksum over concatenation
    start = 1 if value is None else value
    incremental = zlib.adler32(d2, zlib.adler32(d, start))
    whole = zlib.adler32(d + d2, start)
    assert incremental == whole
# End program