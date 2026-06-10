from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=1, max_value=0xffffffff))
def test_adler32_is_always_integer(data, value):
    assert isinstance(zlib.adler32(data, value), int)

@given(st.binary(), st.binary(), st.integers(min_value=1, max_value=0xffffffff))
def test_adler32_changes_with_data(first_data, second_data, value):
    if first_data != second_data:
        assert zlib.adler32(first_data, value) != zlib.adler32(second_data, value)

@given(st.binary(), st.integers(min_value=1, max_value=0xffffffff))
def test_adler32_is_deterministic(data, value):
    assert zlib.adler32(data, value) == zlib.adler32(data, value)

@given(st.binary())
def test_adler32_default_value(data):
    assert zlib.adler32(data) == zlib.adler32(data, 1)

@given(st.binary(), st.integers(min_value=1, max_value=0xffffffff))
def test_adler32_initial_value(data, value):
    assert zlib.adler32(data, value) != zlib.adler32(data) or value == 1
# End program