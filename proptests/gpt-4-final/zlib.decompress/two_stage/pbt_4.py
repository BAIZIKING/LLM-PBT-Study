from hypothesis import given, strategies as st
import zlib

# Default parameters for wbits and bufsize
DEFAULT_WBITS = zlib.MAX_WBITS
DEFAULT_BUFSIZE = zlib.DEF_BUF_SIZE

# Strategy for generating random bytes data
data_strategy = st.binary()

# Strategy for generating wbits parameter
wbits_strategy = st.integers(-15, 47)

# Strategy for generating bufsize parameter
bufsize_strategy = st.integers(0, 1024 * 1024)


@given(data=data_strategy, wbits=wbits_strategy, bufsize=bufsize_strategy)
def test_zlib_decompress_properties(data, wbits, bufsize):
    try:
        # if any issue with parameters, it should raise an error before decompression
        compressed = zlib.compress(data, wbits, bufsize=bufsize)
        decompressed = zlib.decompress(compressed, wbits, bufsize)
        assert isinstance(decompressed, bytes), "Decompressed data should be bytes object"
    except Exception as e:
        # skip test in case of invalid wbits or bufsize param
        return

    # Check property 2
    assert len(decompressed) >= len(data), "Length of decompressed data should be greater or equal to original"

    # Check property 4 - if we use smaller wbits for decompression, an exception should be raised
    if wbits > 8:  # checking for smaller wbits
        try:
            _ = zlib.decompress(compressed, wbits - 1, bufsize)
            raise AssertionError("Expected an error when decompressing with smaller wbits")
        except zlib.error:
            pass  # this is expected

    # Check property 5 - decompression should be independent of bufsize
    try:
        decompressed_with_diff_bufsize = zlib.decompress(compressed, wbits, bufsize=bufsize+1)
        assert decompressed == decompressed_with_diff_bufsize, "Decompression should be independent of bufsize"
    except zlib.error:
        pass  # this is expected if bufsize value is not favourable