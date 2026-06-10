from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1000))
def test_decompress_output_length(compressed_data):
    decompressed_data = zlib.decompress(compressed_data, wbits=-15)
    assert len(decompressed_data) >= len(compressed_data)

@given(st.binary(max_size=1000))
def test_decompress_compress_roundtrip(data):
    compressed_data = zlib.compress(data, level=6)
    decompressed_data = zlib.decompress(compressed_data)
    assert data == decompressed_data

@given(st.binary(max_size=1000), st.integers(min_value=8, max_value=15))
def test_decompress_larger_wbits(data, wbits):
    compressed_data = zlib.compress(data, level=6)
    decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
    assert data == decompressed_data

@given(st.binary(max_size=1000))
def test_decompress_invalid_data(data):
    try:
        zlib.decompress(data)
    except zlib.error:
        pass
    else:
        assert False, "Expected zlib.error for invalid data"

@given(st.binary(max_size=1000))
def test_decompress_no_header_trailer(data):
    compressed_data = zlib.compress(data)[2:-4]  # Remove header and trailer
    decompressed_data = zlib.decompress(compressed_data, wbits=-15)
    assert data == decompressed_data
# End program