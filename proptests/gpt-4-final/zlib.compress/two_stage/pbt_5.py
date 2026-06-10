from hypothesis import given, assume, strategies as st
import zlib

@given(st.binary(), st.integers(-1, 9), st.integers(-15, 31))
def test_zlib_compress_property(data, level, wbits):
    # Avoiding large inputs and overflows for practical purposes
    assume(len(data) <= 1000)
    
    # Test 1: Type of Output.
    compressed = zlib.compress(data, level=level, wbits=wbits)
    assert isinstance(compressed, bytes)    

    # Test 2: Length of Output.
    if level != 0:
        assert len(compressed) <= len(data)
    else:
        assert len(compressed) == len(data)

    # Test 3: Compression Level Control.
    if level > -1 and level <= 9:
        compressed_level_fast = zlib.compress(data, level=1, wbits=wbits)
        compressed_level_best = zlib.compress(data, level=9, wbits=wbits)
        assert len(compressed_level_best) <= len(compressed_level_fast)

    # Test 4: Consistent Output With Same Input.
    another_compressed = zlib.compress(data, level=level, wbits=wbits)
    assert compressed == another_compressed

# Test 5: Error Handling cannot be achieved using hypothesis as it requires assertRaises 
# functionality outside the hypothesis. Therefore another test function needs to be written.
def test_zlib_compress_error():
    with pytest.raises(Exception):
        zlib.compress(b"Some Data", level=1000, wbits=5000)
        zlib.compress(b"Some Data", level=-1000, wbits=-5000)
    
# End program