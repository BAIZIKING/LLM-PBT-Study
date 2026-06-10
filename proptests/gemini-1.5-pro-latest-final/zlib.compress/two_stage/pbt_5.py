from hypothesis import given, strategies as st
import zlib

# Property 1: Output is always a bytes object
@given(st.data())
def test_zlib_compress_output_type(data):
    input_data = data.draw(st.binary())
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(st.integers(min_value=-15, max_value=31))
    compressed_data = zlib.compress(input_data, level=level, wbits=wbits)
    assert isinstance(compressed_data, bytes)

# Property 2: Output length is never greater than input length for level 0
@given(st.data())
def test_zlib_compress_level_0_length(data):
    input_data = data.draw(st.binary())
    compressed_data = zlib.compress(input_data, level=0)
    assert len(compressed_data) <= len(input_data)

# Property 3: Output length is never greater than input length for level 1-9 with wbits <= 0
@given(st.data())
def test_zlib_compress_negative_wbits_length(data):
    input_data = data.draw(st.binary(max_size=1024))  # Limit size to avoid excessive memory usage
    level = data.draw(st.integers(min_value=1, max_value=9))
    wbits = data.draw(st.integers(max_value=0)) 
    compressed_data = zlib.compress(input_data, level=level, wbits=wbits)
    assert len(compressed_data) <= len(input_data) 

# Property 4: Output is decompressible with zlib.decompress()
@given(st.data())
def test_zlib_compress_decompress(data):
    input_data = data.draw(st.binary(max_size=1024))  
    level = data.draw(st.integers(min_value=-1, max_value=9))
    wbits = data.draw(st.integers(min_value=-15, max_value=31)) 
    compressed_data = zlib.compress(input_data, level=level, wbits=wbits)
    decompressed_data = zlib.decompress(compressed_data, -wbits) # Negate wbits for decompression
    assert decompressed_data == input_data

# Property 5: Output length decreases with increasing compression level for same input
@given(st.data())
def test_zlib_compress_level_output_size(data):
    input_data = data.draw(st.binary(min_size=100)) # Ensure enough data for compression difference
    levels = data.draw(
        st.lists(st.integers(min_value=1, max_value=9), min_size=2, unique=True)
    )
    compressed_sizes = [
        len(zlib.compress(input_data, level=level)) for level in levels
    ]
    for i in range(1, len(compressed_sizes)):
        assert compressed_sizes[i] <= compressed_sizes[i - 1] 
# End program