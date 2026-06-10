from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_output_is_bytes(data):
    compressed = zlib.compress(data)
    assert isinstance(compressed, bytes)

@given(st.binary())
def test_output_length(data):
    compressed = zlib.compress(data)
    assert len(compressed) <= len(data)

@given(st.binary(), st.integers(min_value=0, max_value=9), st.integers(min_value=-15, max_value=31))
def test_idempotent_compression(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    recompressed = zlib.compress(compressed, level=level, wbits=wbits)
    assert compressed == recompressed

@given(st.binary(), st.integers(min_value=-15, max_value=31))
def test_round_trip(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert data == decompressed

@given(st.binary(), st.integers(min_value=0, max_value=8), st.integers(min_value=9, max_value=15))
def test_higher_level_smaller_output(data, level1, level2):
    compressed1 = zlib.compress(data, level=level1)
    compressed2 = zlib.compress(data, level=level2)
    if level1 < level2:
        assert len(compressed1) >= len(compressed2)
    else:
        assert len(compressed1) <= len(compressed2)
# End program