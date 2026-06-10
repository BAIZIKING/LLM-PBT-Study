from hypothesis import given, strategies as st
import zlib

@given(st.binary(max_size=1000))
def test_decompress_output_length(data):
    decompressed_data = zlib.decompress(data)
    assert len(decompressed_data) >= len(data)

@given(st.binary(max_size=1000))
def test_compress_decompress_identity(data):
    compressed_data = zlib.compress(data)
    decompressed_data = zlib.decompress(compressed_data)
    assert decompressed_data == data

@given(st.just(b''), st.integers(min_value=-15, max_value=47), st.integers(min_value=1, max_value=1000))
def test_decompress_empty_input(data, wbits, bufsize):
    decompressed_data = zlib.decompress(data, wbits=wbits, bufsize=bufsize)
    assert decompressed_data == b''

@given(st.binary(max_size=1000), st.integers(min_value=8, max_value=15), st.integers(min_value=8, max_value=15))
def test_decompress_output_consistency(data, wbits1, wbits2):
    assume(wbits1 <= wbits2)
    decompressed_data1 = zlib.decompress(data, wbits=wbits1)
    decompressed_data2 = zlib.decompress(data, wbits=wbits2)
    assert decompressed_data1 == decompressed_data2

@given(st.binary(max_size=1000), st.integers(min_value=8, max_value=15))
def test_compress_decompress_round_trip(data, wbits):
    compressed_data = zlib.compress(data, wbits)
    decompressed_data = zlib.decompress(compressed_data, wbits)
    assert decompressed_data == data
# End program