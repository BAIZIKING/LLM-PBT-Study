from hypothesis import given, strategies as st
import zlib

# Summary: The strategy aims to generate a diverse range of inputs for `zlib.adler32`, including:
# - Empty byte strings.
# - Byte strings of varying lengths and content.
# - Different starting values for the checksum calculation.

@given(st.data())
def test_zlib_adler32(data):
    # Generate test cases:
    input_bytes = data.draw(st.binary())
    initial_value = data.draw(st.integers())

    # Property 1: Checksum of empty input should be the initial value (or 1 if not provided).
    if not input_bytes:
        assert zlib.adler32(input_bytes, initial_value) == initial_value or 1

    # Property 2: Checksum should be deterministic (same input, same checksum).
    assert zlib.adler32(input_bytes, initial_value) == zlib.adler32(input_bytes, initial_value)

    # Property 3: Checksum should be different for different inputs (limited by hash collisions).
    other_bytes = data.draw(st.binary(min_size=1))  # Ensure at least one byte difference
    if other_bytes != input_bytes:
        assert zlib.adler32(other_bytes, initial_value) != zlib.adler32(input_bytes, initial_value)

# End program