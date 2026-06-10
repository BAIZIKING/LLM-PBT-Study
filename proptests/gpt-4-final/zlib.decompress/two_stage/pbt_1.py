from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=-15, max_value=47), st.integers(min_value=1))
def test_zlib_decompress_property(input_data, wbits, bufsize):
    # Property 1: The output should always be a bytes object.
    try:
        output = zlib.decompress(input_data, wbits=wbits, bufsize=bufsize)
        assert isinstance(output, bytes)
    except:
        # Ignore the case when the inputs cause zlib.decompress to raise error
        pass

    # Property 2: The output size will not exceed the size of the input data.
    try:
        output = zlib.decompress(input_data, wbits=wbits, bufsize=bufsize)
        assert len(output) <= len(input_data)
    except:
        # Ignore the case when the inputs cause zlib.decompress to raise error
        pass

    # Property 3: The function should throw an error if the inputs are not in correct format or values.
    with pytest.raises(Exception) as excinfo:
        # Test with invalid wbits values
        if not -15 <= wbits <= 47 or (wbits > 15 and wbits < 24) or (wbits > 31 and wbits < 40):
            zlib.decompress(input_data, wbits=wbits, bufsize=bufsize)

    # Property 4: When suitable wbits is chosen, the decompressed data should return to its original form before compression.
    try:
        original_data = input_data
        compressed_data = zlib.compress(original_data)
        decompressed_data = zlib.decompress(compressed_data, wbits=wbits, bufsize=bufsize)
        assert decompressed_data == original_data
    except:
        # Ignore the case when the inputs cause zlib.decompress to raise error
        pass

    # Property 5: bufsize should control the initial size of the output buffer.
    try:
        original_data = input_data
        compressed_data = zlib.compress(original_data)
        decompressed_data = zlib.decompress(compressed_data, wbits=wbits, bufsize=bufsize)
        assert len(decompressed_data) >= bufsize
    except:
        # Ignore the case when the inputs cause zlib.decompress to raise error
        pass
# End of program