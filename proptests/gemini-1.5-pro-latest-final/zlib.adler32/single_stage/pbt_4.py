from hypothesis import given, strategies as st
import zlib

# Summary: The generation strategy aims to create a diverse range of inputs for `zlib.adler32` by considering various data types, lengths, and initial values. 
# It includes edge cases such as empty data, data with different byte values, and different starting values for the checksum.

@given(data=st.data())
def test_zlib_adler32(data):
    # Generate input data:
    input_data = data.draw(st.binary())  # Generate binary data of varying lengths

    # Generate optional starting value:
    start_value = data.draw(st.integers(min_value=0, max_value=2**32 - 1))  # Unsigned 32-bit integer

    # Calculate checksum with and without the starting value:
    checksum_default = zlib.adler32(input_data)
    checksum_with_start = zlib.adler32(input_data, start_value)

    # Property 1: Checksum is an unsigned 32-bit integer
    assert isinstance(checksum_default, int) and checksum_default >= 0 and checksum_default <= 2**32 - 1
    assert isinstance(checksum_with_start, int) and checksum_with_start >= 0 and checksum_with_start <= 2**32 - 1 

    # Property 2: Checksum with starting value is different from default checksum
    if start_value != 1:
        assert checksum_default != checksum_with_start

    # Property 3: Checksum of empty data is 1 (default start value)
    if not input_data:
        assert checksum_default == 1

# End program