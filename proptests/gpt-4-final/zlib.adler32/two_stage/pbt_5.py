from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=1, max_value=4294967295))
def test_output_is_integer(data, value):
    result = zlib.adler32(data, value)
    assert isinstance(result, int)

@given(st.binary(), st.integers(min_value=1, max_value=4294967295))
def test_output_range(data, value):
    result = zlib.adler32(data, value)
    assert 0 <= result <= 4294967295

@given(st.binary())
def test_consistent_results(data):
    result1 = zlib.adler32(data)
    result2 = zlib.adler32(data)
    assert result1 == result2

@given(st.binary(), st.integers(min_value=1, max_value=4294967295))
def test_incorporation_of_initial_value(data, value):
    result_default = zlib.adler32(data)
    result_value = zlib.adler32(data, value)
    if value != 1:
        assert result_default != result_value
    else:
        assert result_default == result_value
# End program