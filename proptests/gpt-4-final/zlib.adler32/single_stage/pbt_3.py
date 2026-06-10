from hypothesis import given, strategies as st
import zlib

@given(st.data())
def test_zlib_adler32(data):
    input1 = data.draw(st.binary(min_size=1))
    input2 = data.draw(st.binary(min_size=1))
    
    # Computing checksums independently
    adler1 = zlib.adler32(input1)
    adler2 = zlib.adler32(input2)
    
    # Computing a running checksum over the concatenation of input1 and input2
    adler_concatenate = zlib.adler32(input1 + input2)
    adler_concatenate_expected = zlib.adler32(input2, adler1)

    # Asserts checksum for concatenated strings matches the expected value
    assert adler_concatenate == adler_concatenate_expected
    
    # Asserts result is an unsigned integer
    assert adler1 >= 0
    assert adler2 >= 0
    assert adler_concatenate >= 0
    assert adler_concatenate_expected >= 0
# End program