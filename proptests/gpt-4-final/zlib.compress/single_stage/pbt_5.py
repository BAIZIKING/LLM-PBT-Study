from hypothesis import given, strategies as st
import zlib

# As we are generating random values for data, level and wbits
# we are not only testing the zlib.compress function for normal cases, but also for edge cases and exceptions
@given(data=st.binary(), level=st.integers(-1, 9), wbits=st.one_of(st.integers(9, 15), st.integers(-15, -9), st.integers(25, 31)))
def test_zlib_compress(data, level, wbits):
    try: # zlib.compress might pass or raise exception, depending on inputs
        compressed = zlib.compress(data, level, wbits)
        assert len(data) >= len(compressed)
        if level == 0:
            assert len(data) == len(compressed)
    except Exception as e: # Test for expected exceptions
        assert isinstance(e, zlib.error)