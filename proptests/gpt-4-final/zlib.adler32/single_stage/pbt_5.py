from hypothesis import given, strategies as st
import zlib

# here we are stating that our function takes two arguments, one is a binary and other is an integer or None
@given(st.binary(), st.one_of(st.integers(), st.none()))
def test_zlib_adler32(data, value):
    # First, capture the output of the function
    result = zlib.adler32(data, value) if value else zlib.adler32(data)

    # Checking if the result is always an unsigned 32-bit integer
    lower_bound = 0
    upper_bound = 2**32 - 1
    assert lower_bound <= result <= upper_bound

    # Checking if the value argument impacts the result
    if value:
        new_result = zlib.adler32(data)
        assert result != new_result