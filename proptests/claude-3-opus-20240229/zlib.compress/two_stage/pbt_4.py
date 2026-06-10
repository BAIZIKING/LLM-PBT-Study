from hypothesis import given, strategies as st
import zlib

@given(data=st.binary(max_size=1000))
def test_output_is_bytes(data):
    compressed = zlib.compress(data)
    assert isinstance(compressed, bytes)

@given(data=st.binary(max_size=1000), level=st.integers(min_value=1, max_value=9))
def test_output_smaller_than_input(data, level):
    compressed = zlib.compress(data, level=level)
    assert len(compressed) <= len(data)

@given(data=st.binary(max_size=1000), level=st.integers(min_value=0, max_value=9), wbits=st.integers(min_value=-15, max_value=31))
def test_compressing_compressed_data(data, level, wbits):
    compressed1 = zlib.compress(data, level=level, wbits=wbits)
    compressed2 = zlib.compress(compressed1, level=level, wbits=wbits)
    assert len(compressed2) >= len(compressed1)

@given(data=st.binary(max_size=1000), wbits=st.integers(min_value=9, max_value=15))
def test_header_and_trailer_included(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    assert compressed.startswith(b'\x78')  # zlib header
    assert compressed.endswith(b'\x00\x00\xff\xff')  # zlib trailer

@given(data=st.binary(max_size=1000), wbits=st.integers(min_value=-15, max_value=31))
def test_decompress_round_trip(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    decompressed = zlib.decompress(compressed, wbits=wbits)
    assert decompressed == data
# End program