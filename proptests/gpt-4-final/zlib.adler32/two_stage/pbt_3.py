from hypothesis import given, strategies as st
import zlib

# Test 1: Invariant Output Range
@given(st.binary())
def test_adler32_output_range(data):
    result = zlib.adler32(data)
    assert 0 <= result <= 4294967295  # Ensure the result is within the range of an unsigned 32-bit integer.

# Test 2: Consistent Results with Default Value
@given(st.binary())
def test_adler32_consistency(data):
    result_1 = zlib.adler32(data)
    result_2 = zlib.adler32(data)
    assert result_1 == result_2  # Ensure consistency with the same data input.
    
# Test 3: Same Checksum for Same Input
@given(st.binary(), st.binary())
def test_adler32_same_input(data1, data2):
    if data1 == data2:  # When data contents are identical
        assert zlib.adler32(data1) == zlib.adler32(data2)
        
# Test 4: Different Checksum for Different Input
@given(st.binary(), st.binary())
def test_adler32_different_input(data1, data2):
    if data1 != data2:  # When data contents are not identical
        assert zlib.adler32(data1) != zlib.adler32(data2)
        
# Test 5: Update with Concatenation
@given(st.binary(), st.binary())
def test_adler32_update_with_concatenation(data1, data2):
    assert zlib.adler32(data1 + data2) == zlib.adler32(data2, zlib.adler32(data1))

# End program