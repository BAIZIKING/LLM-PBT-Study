from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1024))
def test_output_type(data):
    compressed = zlib.compress(data)
    assert isinstance(compressed, bytes)

@given(st.binary(max_size=1024), st.integers(min_value=-1, max_value=9), st.just(zlib.MAX_WBITS))
def test_output_size(data, level, wbits):
    compressed = zlib.compress(data, level=level, wbits=wbits)
    assert len(compressed) <= len(data)

@given(st.binary(max_size=1024), st.integers(min_value=-1, max_value=9), st.just(zlib.MAX_WBITS))
def test_idempotent_compression(data, level, wbits):
    compressed_once = zlib.compress(data, level=level, wbits=wbits)
    compressed_twice = zlib.compress(compressed_once, level=level, wbits=wbits)
    assert len(compressed_twice) >= len(compressed_once)

@given(st.binary(max_size=1024), st.integers(min_value=-1, max_value=8), st.just(zlib.MAX_WBITS))
def test_higher_level_smaller_output(data, level, wbits):
    compressed_lower = zlib.compress(data, level=level, wbits=wbits)
    compressed_higher = zlib.compress(data, level=level+1, wbits=wbits)
    assert len(compressed_higher) <= len(compressed_lower)

@given(st.binary(max_size=1024), st.integers(min_value=9, max_value=15))
def test_wbits_header_trailer(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    assert compressed.startswith(b'\x78')  # zlib header
    assert compressed.endswith(b'\x00\x00\xff\xff')  # zlib trailer

@given(st.binary(max_size=1024), st.integers(min_value=-15, max_value=-9))
def test_wbits_no_header_trailer(data, wbits):
    compressed = zlib.compress(data, wbits=wbits)
    assert not compressed.startswith(b'\x78')  # no zlib header
    assert not compressed.endswith(b'\x00\x00\xff\xff')  # no zlib trailer
# End program