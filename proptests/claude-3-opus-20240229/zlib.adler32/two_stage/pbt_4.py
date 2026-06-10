from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_result_range(data):
    result = zlib.adler32(data)
    assert 0 <= result <= 2**32 - 1

@given(st.integers(min_value=0, max_value=2**32 - 1))
def test_empty_data(value):
    result = zlib.adler32(b'', value)
    assert result == value

@given(st.binary(), st.binary(), st.integers(min_value=0, max_value=2**32 - 1))
def test_concatenation(data1, data2, value):
    result1 = zlib.adler32(data1, value)
    result2 = zlib.adler32(data2, result1)
    combined_result = zlib.adler32(data1 + data2, value)
    assert result2 == combined_result

@given(st.binary(), st.data())
def test_order_independence(data, split):
    split_point = split.draw(st.integers(min_value=0, max_value=len(data)))
    data1, data2 = data[:split_point], data[split_point:]
    result1 = zlib.adler32(data1)
    result2 = zlib.adler32(data2, result1)
    combined_result = zlib.adler32(data)
    assert result2 == combined_result

@given(st.binary(), st.integers(min_value=0, max_value=2**32 - 1))
def test_deterministic(data, value):
    result1 = zlib.adler32(data, value)
    result2 = zlib.adler32(data, value)
    assert result1 == result2
# End program