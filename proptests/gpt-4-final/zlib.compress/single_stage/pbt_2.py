from hypothesis import given, strategies as st
import zlib

# Generating bytes for `data`, integers for `level` and `wbits`.
@given(st.binary(), st.integers(min_value=-1, max_value=9), st.integers(min_value=-15, max_value=31))
def test_zlib_compress(data, level, wbits):
    # Calling the function
    try:
        result = zlib.compress(data, level, wbits)
        # Check if returned object is bytes
        assert isinstance(result, bytes)
    except Exception as error: 
        # If there is any error, print the error message and the input that caused it
        print(f"Input data: {data}, level: {level}, wbits: {wbits}")
        print(f"Error: {error}")
# End program