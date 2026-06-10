from hypothesis import given, strategies as st
import zlib

# Summary: Generate random byte sequences (including empty) with st.binary() and
# random unsigned 32-bit starting values with st.integers(0, 2**32 - 1). Draw a
# split index to test the running-checksum/concatenation property. Verify: result
# is an unsigned 32-bit int, determinism, the default starting value equals 1, and
# that a running checksum over two concatenated parts matches the whole.
@given(st.data())
def test_zlib_adler32(data):
    payload = data.draw(st.binary(min_size=0, max_size=1024))
    value = data.draw(st.integers(min_value=0, max_value=2**32 - 1))

    result = zlib.adler32(payload, value)

    # Property 1: result is an unsigned 32-bit integer
    assert isinstance(result, int)
    assert 0 <= result <= 2**32 - 1

    # Property 2: determinism
    assert zlib.adler32(payload, value) == result

    # Property 3: default starting value is 1
    assert zlib.adler32(payload) == zlib.adler32(payload, 1)

    # Property 4: running checksum over concatenated inputs
    split = data.draw(st.integers(min_value=0, max_value=len(payload)))
    part1, part2 = payload[:split], payload[split:]
    running = zlib.adler32(part2, zlib.adler32(part1, value))
    assert running == result
# End program