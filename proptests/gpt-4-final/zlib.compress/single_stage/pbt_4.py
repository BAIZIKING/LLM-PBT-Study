import zlib
from hypothesis import given, strategies as st

@given(data=st.binary(), level=st.integers(min_value=-1, max_value=9), wbits=st.one_of(st.integers(min_value=9, max_value=15), st.integers(min_value=-9, max_value=-15), st.integers(min_value=25, max_value=31)))
def test_zlib_compress(data, level, wbits):
    result = zlib.compress(data, level, wbits)
    
    # Check result is a bytes object
    assert isinstance(result, bytes)

    # When level is 0, output should equal input
    if level == 0:
        assert result == data

    # When wbits value is larger, resulting byte size should be smaller (we can only compare if wbits is positive)
    if wbits >= 9 and wbits <= 15:
        result_small_wbits = zlib.compress(data, level, 9)
        result_large_wbits = zlib.compress(data, level, 15)
        assert len(result_small_wbits) >= len(result_large_wbits)