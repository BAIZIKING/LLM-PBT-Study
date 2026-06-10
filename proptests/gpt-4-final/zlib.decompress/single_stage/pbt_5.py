from hypothesis import given, strategies as st, assume
import zlib

# Generate bytes data, integer for wbits in its range and for bufsize.
@given(st.binary(min_size=1), st.integers(min_value=-15, max_value=47), st.integers(min_value=0))
def test_zlib_decompress(data, wbits, bufsize):
    # Exclude specific invalid wbits values
    assume(not ((8 > wbits > 15) or (24 > wbits > 31) or (40 > wbits > 47) or (0 < wbits < -15)))

    try:
        # If wbits and bufsize are integers in their allowable ranges, and data is bytes, should not raise an exception.
        zlib.decompress(data, wbits=wbits, bufsize=bufsize)
    except zlib.error:
        # If zlib.error is raised, then wbits is out of its allowable ranges or bufsize is not integer.
        assert ((8 > wbits > 15) or (24 > wbits > 31) or (40 > wbits > 47) or (0 < wbits < -15) or (not isinstance(bufsize, int)))
# End program