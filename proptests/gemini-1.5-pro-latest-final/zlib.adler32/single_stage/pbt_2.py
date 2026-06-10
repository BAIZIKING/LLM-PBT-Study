from hypothesis import given, strategies as st
import zlib

# Summary: This test generates a wide variety of inputs for the zlib.adler32 function, including empty data, data of varying lengths, and data with different starting values. It checks that the output is always an unsigned 32-bit integer and that the function behaves consistently when called multiple times with the same input.
@given(st.data())
def test_zlib_adler32(data):
    # Generate random data and starting values
    input_data = data.draw(st.binary())
    start_value = data.draw(st.integers(min_value=0, max_value=2**32 - 1))

    # Calculate the Adler-32 checksum
    checksum = zlib.adler32(input_data, start_value)

    # Check that the output is an unsigned 32-bit integer
    assert isinstance(checksum, int)
    assert checksum >= 0
    assert checksum <= 2**32 - 1

    # Check consistency of results
    assert zlib.adler32(input_data, start_value) == checksum
    assert zlib.adler32(input_data) == zlib.adler32(input_data, 1)

# End program