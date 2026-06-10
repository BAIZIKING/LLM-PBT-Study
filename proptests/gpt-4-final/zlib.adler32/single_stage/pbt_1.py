import zlib
from hypothesis import given, strategies as st

@given(st.binary(), st.integers(min_value=1, max_value=65535))
def test_zlib_adler32(data, value):
    # Compute Adler-32 checksum without a starting value.
    no_starting_value = zlib.adler32(data)
    # Assert that the result is always an unsigned 32-bit integer.
    assert isinstance(no_starting_value, int) and (0 <= no_starting_value < 2**32)

    # Compute Adler-32 checksum with a starting value.
    with_starting_value = zlib.adler32(data, value)
    # Assert that the result is always an unsigned 32-bit integer.
    assert isinstance(with_starting_value, int) and (0 <= with_starting_value < 2**32)
    # Assert that the two results are different for a majority of cases.
    assert no_starting_value != with_starting_value
# End program