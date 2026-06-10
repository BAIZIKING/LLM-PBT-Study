from hypothesis import given, strategies as st
import zlib

# Generating a wide variety of byte data from length of 0 to 2^32-1
@given(st.binary(min_size=0, max_size=4294967295))
def test_adler32(b):
    result = zlib.adler32(b)
    # Check whether the result is an integer
    assert isinstance(result, int)
    # Check whether the result is within the range [0, 2^32-1]
    assert 0 <= result < 4294967296
# End program