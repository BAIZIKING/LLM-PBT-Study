from hypothesis import given, strategies as st
import zlib

@given(data=st.binary(max_size=1000))
def test_output_type(data):
    assert isinstance(zlib.compress(data), bytes)

@given(data=st.binary(max_size=1000), level=st.integers(min_value=0, max_value=9))
def test_output_length(data, level):
    compressed = zlib.compress(data, level=level)
    if level == 0:
        assert len(compressed) >= len(data)
    else:
        assert len(compressed) <= len(data)

@given(data=st.binary(max_size=1000), wbits=st.integers(min_value=-15, max_value=15))
def test_roundtrip(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data

@given(data=st.binary(max_size=1000), level1=st.integers(min_value=1, max_value=8), level2=st.integers(min_value=1, max_value=9))
def test_compression_level(data, level1, level2):
    assume(level1 < level2)
    compressed1 = zlib.compress(data, level=level1)
    compressed2 = zlib.compress(data, level=level2)
    assert len(compressed2) <= len(compressed1)

@given(data=st.binary(max_size=1000), level=st.integers(min_value=-1, max_value=9), wbits=st.integers(min_value=-15, max_value=15))
def test_deterministic_output(data, level, wbits):
    compressed1 = zlib.compress(data, level=level, wbits=wbits)
    compressed2 = zlib.compress(data, level=level, wbits=wbits)
    assert compressed1 == compressed2
# End program