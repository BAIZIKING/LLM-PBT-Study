from hypothesis import given, strategies as st
import zlib

# Summary: Generate `data` as arbitrary byte strings (covering empty and large)
# and an optional `value` as a 32-bit unsigned int (including boundaries 0 and
# 2**32-1) or None to exercise the default starting value of 1. Verify the
# result is always an unsigned 32-bit int, the default equals value=1,
# the concatenation/running-checksum property holds, and results are deterministic.
@given(st.data())
def test_zlib_adler32(data):
    UINT32_MAX = 2**32 - 1

    a = data.draw(st.binary(max_size=512))
    b = data.draw(st.binary(max_size=512))
    value = data.draw(st.one_of(st.none(), st.integers(min_value=0, max_value=UINT32_MAX)))

    # Compute checksum, with or without the optional starting value.
    if value is None:
        result = zlib.adler32(a)
    else:
        result = zlib.adler32(a, value)

    # Property 1: result is always an unsigned 32-bit integer.
    assert isinstance(result, int)
    assert 0 <= result <= UINT32_MAX

    # Property 2: omitting value is equivalent to value=1 (the documented default).
    assert zlib.adler32(a) == zlib.adler32(a, 1)

    # Property 3: running checksum over concatenation matches whole-input checksum.
    incremental = zlib.adler32(b, zlib.adler32(a))
    whole = zlib.adler32(a + b)
    assert incremental == whole

    # Property 4: determinism - same inputs yield the same output.
    if value is None:
        assert zlib.adler32(a) == result
    else:
        assert zlib.adler32(a, value) == result
# End program