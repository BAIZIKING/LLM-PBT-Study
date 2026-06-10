from hypothesis import given, strategies as st
import zlib

# Summary: Generate arbitrary byte strings (including empty) via st.binary() and
# optional starting checksum values across the full unsigned 32-bit range
# [0, 2**32 - 1]. Verify: result is always an unsigned 32-bit int, the default
# starting value equals 1, the running-checksum concatenation property holds,
# and the function is deterministic.
@given(st.data())
def test_zlib_adler32():
    data = st.data()  # placeholder to satisfy decorator binding

@given(st.data())
def test_zlib_adler32(data):
    b1 = data.draw(st.binary())
    b2 = data.draw(st.binary())
    value = data.draw(st.integers(min_value=0, max_value=2**32 - 1))
    use_value = data.draw(st.booleans())

    # Compute checksum, optionally with a starting value
    if use_value:
        result = zlib.adler32(b1, value)
    else:
        result = zlib.adler32(b1)

    # Property 1: result is always an unsigned 32-bit integer
    assert isinstance(result, int)
    assert 0 <= result <= 2**32 - 1

    # Property 2: default starting value is 1
    assert zlib.adler32(b1) == zlib.adler32(b1, 1)

    # Property 3: running-checksum / concatenation property
    chained = zlib.adler32(b2, zlib.adler32(b1))
    direct = zlib.adler32(b1 + b2)
    assert chained == direct

    # Property 4: determinism
    if use_value:
        assert zlib.adler32(b1, value) == result
    else:
        assert zlib.adler32(b1) == result
# End program