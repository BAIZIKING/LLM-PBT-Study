from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating compressed data
# Limit data size and window sizes to avoid overflows and excessive runtime
@st.composite
def compressed_data(draw):
    data = draw(st.binary(max_size=1024))
    wbits = draw(st.integers(min_value=8, max_value=15))
    compress_obj = zlib.compressobj(wbits=wbits)
    compressed_data = compress_obj.compress(data) + compress_obj.flush()
    return compressed_data, wbits

@given(compressed_data())
def test_decompress_length(data_and_wbits):
    compressed_data, wbits = data_and_wbits
    decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
    # Property 1: Decompressed data can be larger or smaller depending on compression level
    assert len(decompressed_data) >= len(compressed_data) 

@given(compressed_data())
def test_decompress_idempotence(data_and_wbits):
    compressed_data, wbits = data_and_wbits
    decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
    double_decompressed_data = zlib.decompress(decompressed_data, wbits=wbits)
    # Property 2: Idempotence
    assert decompressed_data == double_decompressed_data

@given(st.binary(max_size=1024), st.integers(min_value=8, max_value=15))
def test_compress_decompress_integrity(data, wbits):
    compress_obj = zlib.compressobj(wbits=wbits)
    compressed_data = compress_obj.compress(data) + compress_obj.flush()
    decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
    # Property 3: Data Integrity
    assert data == decompressed_data 

@given(st.binary(max_size=1024))
def test_header_influence(data):
    # Compress with and without header/trailer
    compressed_with_header = zlib.compress(data) 
    compressed_without_header = zlib.compress(data, wbits=-15)
    # Decompress both with and without header requirement
    decompressed_with_header = zlib.decompress(compressed_with_header)
    decompressed_without_header = zlib.decompress(compressed_without_header, wbits=-15)
    # Property 4: Header Influence
    assert decompressed_with_header == decompressed_without_header

@given(st.binary(max_size=1024))
def test_incorrect_wbits_error(data):
    # Compress with the maximum window size
    compressed_data = zlib.compress(data, wbits=15)
    # Attempt to decompress with a smaller window size
    with pytest.raises(zlib.error):
        zlib.decompress(compressed_data, wbits=8) 
# End program