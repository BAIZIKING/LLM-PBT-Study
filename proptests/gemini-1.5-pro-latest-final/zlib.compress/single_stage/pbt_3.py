from hypothesis import given, strategies as st
import zlib
import gzip

# Summary: Generates diverse bytestrings, compression levels, and wbits values to test zlib.compress behavior comprehensively.
@given(data=st.binary(), level=st.integers(min_value=-1, max_value=9), wbits=st.one_of(
    st.integers(min_value=9, max_value=15),
    st.integers(min_value=-15, max_value=-9),
    st.integers(min_value=25, max_value=31),
    st.just(15)  # Include default value
))
def test_zlib_compress(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)

    # Check output type and error handling
    assert isinstance(compressed, bytes)

    # Check decompression behavior based on wbits
    if 9 <= wbits <= 15:
        decompressed = zlib.decompress(compressed, wbits=wbits)
    elif -15 <= wbits <= -9:
        decompressed = zlib.decompress(compressed, wbits=-wbits)
    else:
        decompressed = gzip.decompress(compressed)

    assert decompressed == data

    # Check compression level effect (except for level 0)
    if level != 0:
        original_size = len(data)
        compressed_size = len(compressed)
        assert compressed_size < original_size, f"Compression level {level} did not reduce size (original: {original_size}, compressed: {compressed_size})"

# End program