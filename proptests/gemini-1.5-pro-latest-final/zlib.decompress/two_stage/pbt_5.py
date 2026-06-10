from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating compressed data with varying window sizes
@st.composite
def compressed_data(draw):
    data = draw(st.binary())
    wbits = draw(st.integers(min_value=8, max_value=15))  # Limit window size for feasibility
    level = draw(st.integers(min_value=1, max_value=9))  # Compression level
    return zlib.compress(data, level=level, wbits=wbits)

@given(compressed_data())
def test_decompress_length_nonnegative(compressed):
    decompressed = zlib.decompress(compressed)
    assert len(decompressed) >= 0

@given(compressed_data())
def test_decompress_idempotence(compressed):
    decompressed = zlib.decompress(compressed)
    double_decompressed = zlib.decompress(decompressed)
    assert decompressed == double_decompressed

@given(st.binary(), st.integers(min_value=8, max_value=15), st.integers(min_value=1, max_value=9))
def test_decompress_data_preservation(data, wbits, level):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert data == decompressed

@given(st.binary(), st.integers(min_value=-15, max_value=-8))  # Raw data (no zlib header/trailer)
def test_decompress_header_mismatch(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    with pytest.raises(zlib.error):
        zlib.decompress(compressed, wbits=wbits+16)  # Force a header mismatch

@given(st.binary(), st.integers(min_value=8, max_value=15))
def test_decompress_window_size_too_small(data, wbits_compress):
    compressed = zlib.compress(data, wbits=wbits_compress) 
    wbits_decompress = wbits_compress - 1  # Smaller window
    with pytest.raises(zlib.error):
        zlib.decompress(compressed, wbits=wbits_decompress)
# End program