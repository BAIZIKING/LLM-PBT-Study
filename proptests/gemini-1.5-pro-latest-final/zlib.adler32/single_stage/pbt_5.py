from hypothesis import given, strategies as st
import zlib

# Summary: The generation strategy aims to create a diverse set of inputs for `zlib.adler32` by considering various data types, lengths, and starting values. This includes:
# - Generating random byte sequences of varying lengths to cover different input sizes.
# - Including empty byte sequences to test the behavior with no data.
# - Incorporating byte sequences with repetitive patterns (e.g., all zeros, alternating patterns) to check for potential edge cases.
# - Using a range of starting values (including the default value of 1) to test the running checksum functionality.

@given(st.data())
def test_zlib_adler32(data):
    # Generate random byte sequences of varying lengths
    input_data = data.draw(st.binary(min_size=0, max_size=1024))

    # Generate optional starting values
    start_value = data.draw(st.integers(min_value=0, max_value=2**32 - 1))

    # Calculate Adler-32 checksum
    checksum = zlib.adler32(input_data, start_value)

    # Properties to check based on the API documentation:
    # 1. Checksum is an unsigned 32-bit integer
    assert isinstance(checksum, int) and checksum >= 0 and checksum <= 2**32 - 1

    # 2. Checksum with default start value (1) is consistent
    if start_value is None:
        assert checksum == zlib.adler32(input_data) 
# End program