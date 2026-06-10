from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=-1, max_value=9), st.integers(min_value=-15, max_value=31))
def test_zlib_compress_property(input_data, level, wbits):
    try:
        compressed_data = zlib.compress(input_data, level, wbits)
    except Exception as e:
        assert False, 'Unexpected error: {}'.format(str(e))
    
    # Property 1: The output is always a bytes object.
    assert isinstance(compressed_data, bytes), 'Output is not a bytes object'

    # Property 2: When level changes compression level changes but not the data type.
    if level != -1:
        changed_level_data = zlib.compress(input_data, level - 1 if level != 0 else level + 1, wbits)
        assert isinstance(changed_level_data, bytes), 'Data type changed on level adjustment'
        assert len(changed_level_data) != len(compressed_data), 'Compression level did not change on level adjustment'

    # Property 3: The wbits value setting testing
    if wbits > 0 and wbits <= 15:
        # adjusting wbits to have gzip header and footer
        changed_wbits_data = zlib.compress(input_data, level, wbits + 16)
        assert isinstance(changed_wbits_data, bytes), 'Data type changed on wbits adjustment'
        assert len(changed_wbits_data) > len(compressed_data), 'gzip header and footer not detected on wbits adjustment'

    # Property 5: The output size should always be less than or equal to input size if level != 0 
    if level != 0:
        assert len(compressed_data) <= len(input_data), 'Output size is more than input size data'
    
# End program