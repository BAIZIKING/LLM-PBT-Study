from hypothesis import given, strategies as st
import zlib

# Define strategies for valid and invalid compressed data
valid_compressed_data = st.binary(min_size=1)
invalid_compressed_data = st.text() | st.integers() | st.floats()

# Define strategies for wbits parameter
valid_wbits = st.integers(min_value=-15, max_value=47)
invalid_wbits = st.integers(max_value=-16) | st.integers(min_value=48) 

@given(valid_compressed_data, valid_wbits)
def test_decompress_output_type(data, wbits):
    decompressed_data = zlib.decompress(data, wbits=wbits)
    assert isinstance(decompressed_data, bytes)

@given(valid_compressed_data, valid_wbits)
def test_decompress_size_relation(data, wbits):
    decompressed_data = zlib.decompress(data, wbits=wbits)
    assert len(decompressed_data) >= len(data)

@given(valid_compressed_data, valid_wbits)
def test_decompress_idempotence(data, wbits):
    first_decompression = zlib.decompress(data, wbits=wbits)
    second_decompression = zlib.decompress(first_decompression, wbits=wbits)
    assert first_decompression == second_decompression

@given(valid_compressed_data, valid_wbits)
def test_decompress_consistency(data, wbits):
    first_decompression = zlib.decompress(data, wbits=wbits)
    second_decompression = zlib.decompress(data, wbits=wbits)
    assert first_decompression == second_decompression 

@given(invalid_compressed_data | st.tuples(valid_compressed_data, invalid_wbits))
def test_decompress_error_on_invalid_input(data_and_wbits):
    if isinstance(data_and_wbits, tuple):
        data, wbits = data_and_wbits
    else:
        data, wbits = data_and_wbits, 15 # Default wbits 
    with pytest.raises(Exception):
        zlib.decompress(data, wbits=wbits)
# End program