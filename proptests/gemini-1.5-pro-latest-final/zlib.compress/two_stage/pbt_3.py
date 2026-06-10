@given(st.binary(max_size=1024), st.integers(min_value=-15, max_value=15))
def test_zlib_compress_deterministic_output_length(data, wbits):
    compressed_data_1 = zlib.compress(data, level=6, wbits=wbits)
    compressed_data_2 = zlib.compress(data, level=6, wbits=wbits)
    assert len(compressed_data_1) == len(compressed_data_2) 
# End program 