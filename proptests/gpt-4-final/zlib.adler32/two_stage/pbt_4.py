from hypothesis import given, strategies as st
import zlib

# Given binary data and an optional starting value as inputs
@given(st.binary(), st.integers(min_value=0, max_value=2**32-1))
def test_consistency_checksum(data, start_val):
    assert zlib.adler32(data, start_val) == zlib.adler32(data, start_val)

# Type checking
@given(st.binary(), st.integers(min_value=0, max_value=2**32-1))
def test_result_type(data, start_val):
    assert isinstance(zlib.adler32(data, start_val), int)

# Verifying the use of default value vs starting value
@given(st.binary())
def test_default_value(data):
    assert zlib.adler32(data) == zlib.adler32(data, 1)

# Range checking
@given(st.binary(), st.integers(min_value=0, max_value=2**32-1))
def test_checksum_range(data, start_val):
    result = zlib.adler32(data, start_val)
    assert 0 <= result <= 2**32-1

# Calculating checksum over concatenated input
@given(st.binary(), st.binary(), st.integers(min_value=0, max_value=2**32-1))
def test_cumulative_property(data1, data2, start_val):
    combined_result = zlib.adler32(data1 + data2, start_val)
    sequence_result = zlib.adler32(data2, zlib.adler32(data1,start_val))
    assert combined_result == sequence_result
# End program