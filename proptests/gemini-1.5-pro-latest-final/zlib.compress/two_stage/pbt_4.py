from hypothesis import given, strategies as st
import zlib

# Define strategies for data and compression parameters
data_strategy = st.binary(max_size=1024)  # Limit data size to avoid excessive memory usage
level_strategy = st.integers(min_value=-1, max_value=9)
wbits_strategy = st.integers(min_value=-15, max_value=31)


@given(data_strategy, level_strategy, wbits_strategy)
def test_output_type_bytes(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    assert isinstance(compressed, bytes)
# End program

@given(data_strategy, level_strategy, wbits_strategy)
def test_output_length(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    # Exception for Z_NO_COMPRESSION: output might be slightly larger
    if level == 0:
        assert len(compressed) >= len(data)
    else:
        assert len(compressed) <= len(data)
# End program

@given(data_strategy, level_strategy, wbits_strategy.filter(lambda x: 9 <= x <= 15 or -15 <= x <= -9))
def test_decompression_consistency(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data
# End program

@given(data_strategy, wbits_strategy)
def test_compression_level_impact(data, wbits):
    compressed_best_speed = zlib.compress(data, level=1, wbits=wbits)
    compressed_best_compression = zlib.compress(data, level=9, wbits=wbits)
    assert len(compressed_best_compression) <= len(compressed_best_speed)
# End program

@given(data_strategy, level_strategy)
def test_window_size_impact(data, level):
    compressed_small_window = zlib.compress(data, level=level, wbits=9)
    compressed_large_window = zlib.compress(data, level=level, wbits=15)
    # Larger window size might not always result in smaller output, but it's a general trend
    assert len(compressed_large_window) <= len(compressed_small_window) 
# End program