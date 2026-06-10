from hypothesis import given, strategies as st
import zlib

# Define strategies for generating relevant data
data_strategy = st.binary(max_size=1024)  # Limit data size to prevent large inputs
wbits_strategy = st.integers(min_value=-15, max_value=47)

@given(data_strategy)
def test_decompress_output_length(data):
    # Property 1: Output Length is non-negative
    decompressed_data = zlib.decompress(data)
    assert len(decompressed_data) >= 0

@given(data_strategy, wbits_strategy)
def test_decompress_idempotence(data, wbits):
    # Property 2: Idempotence
    decompressed_data = zlib.decompress(data, wbits=wbits)
    doubly_decompressed_data = zlib.decompress(decompressed_data, wbits=wbits)
    assert decompressed_data == doubly_decompressed_data 

@given(st.text())
def test_decompress_data_preservation(text):
    # Property 3: Data Preservation (for lossless compression)
    compressed_data = zlib.compress(text.encode())
    decompressed_data = zlib.decompress(compressed_data)
    assert decompressed_data.decode() == text

@given(data_strategy, wbits_strategy)
def test_decompress_header_influence(data, wbits):
    # Property 4: Header Influence - Testing specific behavior requires knowledge of the compression format 
    # and header/trailer structure. This test serves as a placeholder.
    try:
        decompressed_data = zlib.decompress(data, wbits=wbits)
        # Add assertions based on expected behavior with different wbits values
    except zlib.error:
        # Capture errors due to incorrect header/trailer format
        pass

@given(st.text())
def test_decompress_window_size(text):
    # Property 5: Window Size - Error when window size is too small 
    compressed_data = zlib.compress(text.encode(), wbits=15)  # Use maximum window size for compression 
    with pytest.raises(zlib.error):
        zlib.decompress(compressed_data, wbits=9)  # Use a smaller window size for decompression
# End program 