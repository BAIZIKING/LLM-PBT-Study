from hypothesis import given, strategies as st
import zlib

@given(data=st.binary(), level=st.integers(-1, 9), wbits=st.one_of(st.integers(9, 15), st.integers(-9, -15), st.integers(25, 31)))
def test_zlib_compress(data, level, wbits):
    try:
        compressed_data = zlib.compress(data, level, wbits)
        assert len(compressed_data) <= len(data)
    except Exception as e:
        assert False, str(e)