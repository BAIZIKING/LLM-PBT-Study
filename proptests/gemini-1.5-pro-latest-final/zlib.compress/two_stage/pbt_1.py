from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1024)) # Limit data size to avoid excessive memory usage
def test_output_is_bytes(data):
    compressed = zlib.compress(data)
    assert isinstance(compressed, bytes)

@given(st.binary(max_size=1024))
def test_output_length_no_compression(data):
    compressed = zlib.compress(data, level=0)
    assert len(compressed) <= len(data) + 10 # Allow for small header/trailer

@given(st.binary(max_size=1024))
def test_output_length_incompressible(data):
    # Generate random data, which is likely incompressible
    random_data = bytes(st.integers(min_value=0, max_value=255).example() for _ in range(len(data)))
    compressed = zlib.compress(random_data, level=9)
    assert len(compressed) <= len(random_data) + 10 # Allow for small header/trailer

@given(st.binary(min_size=100, max_size=1024)) # Ensure enough data for potential compression
def test_higher_level_smaller_output(data):
    compressed_low = zlib.compress(data, level=1)
    compressed_high = zlib.compress(data, level=9)
    assert len(compressed_high) <= len(compressed_low)

@given(st.binary(max_size=1024), st.integers(min_value=-15, max_value=15))
def test_decompress_reverses_compress(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data
# End program