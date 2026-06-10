from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=1, max_value=0xFFFFFFFF))
def test_zlib_adler32_property(data, value):
    checksum = zlib.adler32(data, value)

    # Property 1: The function should always return an integer.
    assert isinstance(checksum, int)

    # Property 2: When the function is given the same input, it should always generate the same checksum.
    same_checksum = zlib.adler32(data, value)
    assert checksum == same_checksum

    # Property 3: Even a small changes to the input data should result in a different checksum.
    altered_data = data + b'0'
    altered_checksum = zlib.adler32(altered_data, value)
    assert checksum != altered_checksum

    # Property 4: If no second 'value' argument is provided, the checksum should start from a value of 1.
    default_checksum = zlib.adler32(data)
    assert default_checksum == zlib.adler32(data, 1)

    # Property 5: An Adler-32 checksum should always be of length 32-bit.
    assert 0 <= checksum < 2**32
# End program