from hypothesis import given, strategies as st
import zlib

# Property 1: Output Type
@given(data=st.binary(), level=st.integers(min_value=-1, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_output_type(data, level, wbits):
    output = zlib.compress(data, level, wbits)
    assert isinstance(output, bytes)

# Property 2: Output Size and Compression Level
@given(data=st.binary(min_size=1000), level1=st.integers(min_value=0, max_value=9), level2=st.integers(min_value=0, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_output_size_and_compression_level(data, level1, level2, wbits):
    output1 = zlib.compress(data, level1, wbits)
    output2 = zlib.compress(data, level2, wbits)
    if level1 > level2:
        assert len(output1) < len(output2)
    elif level1 < level2:
        assert len(output1) > len(output2)

# Property 3: Empty Data Handling
@given(level=st.integers(min_value=-1, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_empty_data_handling(level, wbits):
    output = zlib.compress(b'', level, wbits)
    assert isinstance(output, bytes)

# Property 4: Compression Reversibility
@given(data=st.binary(), level=st.integers(min_value=-1, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_compression_reversibility(data, level, wbits):
    compressed = zlib.compress(data, level, wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert data == decompressed

# Property 5: Output with Different 'wbits'
@given(data=st.binary(), level=st.integers(min_value=-1, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_output_with_different_wbits(data, level, wbits):
    output = zlib.compress(data, level, wbits)

    if 9 <= wbits <= 15:
        assert output.startswith(b'\x78')
    elif -15 <= wbits <= -9:
        assert not output.startswith(b'\x78')
    elif 25 <= wbits <= 31:
        assert output.startswith(b'\x1f\x8b')