from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating data and compression levels
data_and_level = st.tuples(
    st.binary(max_size=1024),  # Limit data size to avoid excessive memory usage
    st.integers(min_value=0, max_value=9),
)

@given(data_and_level)
def test_output_is_bytes(data_and_level):
    data, level = data_and_level
    compressed = zlib.compress(data, level=level)
    assert isinstance(compressed, bytes)

@given(data_and_level)
def test_level_zero_length(data_and_level):
    data, level = data_and_level
    if level == 0:
        compressed = zlib.compress(data, level=level)
        assert len(compressed) <= len(data)

@given(data_and_level)
def test_compression_increases_with_level(data_and_level):
    data, level = data_and_level
    if level > 0:
        compressed_lower = zlib.compress(data, level=level-1)
        compressed_higher = zlib.compress(data, level=level)
        assert len(compressed_higher) <= len(compressed_lower)

@given(data_and_level)
def test_decompression_yields_original(data_and_level):
    data, level = data_and_level
    compressed = zlib.compress(data, level=level)
    decompressed = zlib.decompress(compressed)
    assert decompressed == data

@given(st.binary(max_size=1024), st.integers(min_value=-15, max_value=31))
def test_wbits_does_not_affect_decompression(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    decompressed = zlib.decompress(compressed)
    assert decompressed == data
# End program 