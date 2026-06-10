from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_output_is_bytes(data):
    compressed = zlib.compress(data)
    assert isinstance(compressed, bytes)

@given(st.binary(), st.integers(min_value=1, max_value=9))
def test_output_length(data, level):
    compressed = zlib.compress(data, level=level)
    assert len(compressed) <= len(data)

@given(st.binary())
def test_no_compression(data):
    compressed = zlib.compress(data, level=0)
    assert compressed == data

@given(st.binary(), st.integers(min_value=9, max_value=15))
def test_wbits_header_trailer(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    assert compressed.startswith(b'\x78')  # zlib header
    assert compressed.endswith(b'\x00\x00\xff\xff')  # zlib trailer

@given(st.binary(), st.integers(min_value=-15, max_value=-9))
def test_wbits_raw_stream(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    assert not compressed.startswith(b'\x78')  # no zlib header
    assert not compressed.endswith(b'\x00\x00\xff\xff')  # no zlib trailer
# End program