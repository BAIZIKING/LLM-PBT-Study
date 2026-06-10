from hypothesis import given, strategies as st
import zlib

@given(data=st.binary(max_size=1024), wbits=st.integers(min_value=8, max_value=15))
def test_zlib_decompress_roundtrip(data, wbits):
    compressed = zlib.compress(data, wbits)
    decompressed = zlib.decompress(compressed, wbits)
    assert decompressed == data

@given(data=st.binary(max_size=1024))
def test_zlib_decompress_length(data):
    compressed = zlib.compress(data)
    decompressed = zlib.decompress(compressed)
    assert len(decompressed) >= len(compressed) or len(data) == 0

@given(data=st.binary(max_size=1024), wbits=st.integers(min_value=8, max_value=15))
def test_zlib_decompress_valid_zlib_header_trailer(data, wbits):
    compressed = zlib.compress(data, wbits)
    assert zlib.decompress(compressed, wbits)

@given(data=st.binary(max_size=1024), wbits=st.integers(min_value=24, max_value=31))
def test_zlib_decompress_valid_gzip_header_trailer(data, wbits):
    compressed = zlib.compress(data, wbits)
    assert zlib.decompress(compressed, wbits)

@given(data=st.binary(max_size=1024), bufsize=st.integers(min_value=1, max_value=1024))
def test_zlib_decompress_output_consistency(data, bufsize):
    compressed = zlib.compress(data)
    decompressed1 = zlib.decompress(compressed, bufsize=bufsize)
    decompressed2 = zlib.decompress(compressed, bufsize=bufsize)
    assert decompressed1 == decompressed2
# End program