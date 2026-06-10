from hypothesis import given, strategies as st
import zlib

# Summary: Generates diverse inputs for zlib.decompress and checks decompression behavior.
@given(
    data=st.binary(),
    wbits=st.integers(min_value=-15, max_value=47),
    bufsize=st.integers(min_value=1),
)
def test_zlib_decompress(data, wbits, bufsize):
    try:
        decompressed = zlib.decompress(data, wbits=wbits, bufsize=bufsize)
        # Check output type and data integrity (if possible)
        assert isinstance(decompressed, bytes)
        if 8 <= wbits <= 15:
            compressed = zlib.compress(decompressed, level=6, wbits=wbits)
            assert zlib.decompress(compressed, wbits=wbits) == decompressed
    except zlib.error:
        # Check for expected errors with invalid inputs
        assert wbits not in range(8, 16) and wbits not in range(-8, 0)

# End program