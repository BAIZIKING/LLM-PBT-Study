from zlib import adler32
from hypothesis import given, assume, strategies as st

@given(st.binary(), st.integers(min_value=1, max_value=0xffffffff))
def test_zlib_adler32(input_data, value):
    # Calling adler32 with just the input data
    checksum_1 = adler32(input_data)
    # Calling adler32 with input data and a specific starting value
    checksum_2 = adler32(input_data, value)

    # Check that adler32 always returns an unsigned 32-bit integer
    assert 0 <= checksum_1 < 2**32
    assert 0 <= checksum_2 < 2**32

    # Check that identical inputs give identical outputs
    assert checksum_1 == adler32(input_data)

    # Check that different inputs generally give different outputs
    assert (input_data == b"" and value == 1) or checksum_1 != checksum_2