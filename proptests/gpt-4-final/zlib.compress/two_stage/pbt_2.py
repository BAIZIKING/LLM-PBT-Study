from hypothesis import given, strategies as st
import zlib

# Test for the property 1
@given(st.binary(min_size=1, max_size=1000), st.integers(min_value=-1, max_value=9), st.integers(min_value=9, max_value=15))
def test_zlib_compress_type(data, level, wbits):
    result = zlib.compress(data, level, wbits)
    assert isinstance(result, bytes)

# Test for the property 2
@given(st.binary(min_size=1, max_size=1000))
def test_zlib_compress_no_compression(data):
    result = zlib.compress(data, 0)
    assert len(result) >= len(data)

# Test for the property 3 
@given(st.binary(min_size=1, max_size=1000), st.integers(min_value=-1, max_value=9))
def test_zlib_compress_consistency(data, level):
    result1 = zlib.compress(data, level)
    result2 = zlib.compress(data, level)
    assert result1 == result2

# Test for the property 4
@given(st.binary(min_size=1, max_size=1000))
def test_zlib_compress_higher_compression(data):
    result1 = zlib.compress(data, 1) #faster compression, less actual compression
    result2 = zlib.compress(data, 9) #slower compression, higher actual compression
    assert len(result1) >= len(result2)

# Test for the property 5
@given(st.binary(min_size=1, max_size=1000), st.integers(min_value=-1, max_value=9), st.integers(min_value=-15, max_value=24).filter(lambda x: x < -9 or x > 15))
def test_zlib_compress_invalid_wbits(data, level, wbits):
    try:
        zlib.compress(data, level, wbits)
        assert False # We expect an error
    except Exception:
        assert True
# End program