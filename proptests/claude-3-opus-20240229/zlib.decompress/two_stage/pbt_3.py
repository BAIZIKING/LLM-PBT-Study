from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_output_is_bytes(data):
    assert isinstance(zlib.decompress(data), bytes)

@given(st.binary())
def test_output_length_greater_equal_input_length(data):
    assert len(zlib.decompress(data)) >= len(data)

@given(st.binary(), st.integers(min_value=8, max_value=15))
def test_compress_decompress_equality(data, wbits):
    compressed = zlib.compress(data, wbits)
    assert zlib.decompress(compressed, wbits) == data

@given(st.binary(min_size=1), st.integers(min_value=8, max_value=15))
def test_valid_header_trailer_no_error(data, wbits):
    compressed = zlib.compress(data, wbits)
    try:
        zlib.decompress(compressed, wbits)
    except zlib.error:
        assert False, "Decompression raised an error"

@given(st.binary(min_size=1), st.integers(min_value=8, max_value=15), st.integers(max_value=7))
def test_smaller_wbits_raises_error(data, compress_wbits, decompress_wbits):
    compressed = zlib.compress(data, compress_wbits)
    try:
        zlib.decompress(compressed, decompress_wbits)
        assert False, "Decompression should raise an error"
    except zlib.error:
        pass
# End program