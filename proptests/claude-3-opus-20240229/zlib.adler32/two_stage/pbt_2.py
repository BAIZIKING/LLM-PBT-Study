from hypothesis import given, strategies as st
import zlib

@given(st.binary())
def test_unsigned_32bit_result(data):
    assert 0 <= zlib.adler32(data) <= 2**32 - 1

@given(st.binary())
def test_default_value(data):
    assert zlib.adler32(data) == zlib.adler32(data, 1)

@given(st.just(b''))
def test_empty_input(data):
    assert zlib.adler32(data) == 1

@given(st.binary(), st.integers(min_value=0, max_value=2**32-1))
def test_deterministic(data, value):
    assert zlib.adler32(data, value) == zlib.adler32(data, value)

@given(st.binary(), st.binary())
def test_concatenation(data1, data2):
    assert zlib.adler32(data1 + data2) == zlib.adler32(data2, zlib.adler32(data1))
# End program