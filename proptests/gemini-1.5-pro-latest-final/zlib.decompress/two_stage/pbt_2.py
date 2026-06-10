from hypothesis import given, strategies as st
import zlib

# Define strategies for data generation
data_strategy = st.binary(max_size=1024)  # Limit data size to avoid large inputs
wbits_strategy = st.integers(min_value=-15, max_value=47)

@given(data_strategy)
def test_output_length_non_negative(data):
    """Output length of decompressed data should be non-negative."""
    decompressed_data = zlib.decompress(data)
    assert len(decompressed_data) >= 0

@given(data_strategy, wbits_strategy)
def test_idempotence(data, wbits):
    """Decompressing the output again should result in the same data."""
    decompressed_data = zlib.decompress(data, wbits=wbits)
    doubly_decompressed_data = zlib.decompress(decompressed_data, wbits=wbits)
    assert decompressed_data == doubly_decompressed_data

@given(data_strategy)
def test_data_preservation(data):
    """Decompressing compressed data should yield the original data."""
    compressed_data = zlib.compress(data)
    decompressed_data = zlib.decompress(compressed_data)
    assert data == decompressed_data

@given(data_strategy, wbits_strategy)
def test_error_on_wrong_wbits(data, wbits):
    """Incorrect wbits for the format should raise an error."""
    try:
        zlib.decompress(data, wbits=wbits)
        # Check if wbits is valid for the given data format
        if not (-15 <= wbits <= -8 or 8 <= wbits <= 15 or 24 <= wbits <= 31 or 40 <= wbits <= 47):
            assert False, f"Expected error with wbits={wbits}"
    except zlib.error:
        pass  # Expected error

@given(data_strategy, st.integers(min_value=8, max_value=15))
def test_window_size_limitation(data, window_size):
    """Window size smaller than compression size should raise an error."""
    compressed_data = zlib.compress(data, wbits=window_size)
    smaller_window_size = window_size - 1
    with pytest.raises(zlib.error):
        zlib.decompress(compressed_data, wbits=smaller_window_size)
# End program