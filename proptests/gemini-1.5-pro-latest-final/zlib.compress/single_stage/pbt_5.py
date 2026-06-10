from hypothesis import given, strategies as st
import zlib

# Summary: Generates random byte sequences, compression levels, and window sizes 
# to test various aspects of zlib.compress behavior.
@given(
    data=st.binary(),
    level=st.one_of(st.integers(0, 9), st.just(-1)),
    wbits=st.one_of(
        st.integers(9, 15), st.integers(-15, -9), st.integers(25, 31)
    ),
)
def test_zlib_compress(data, level, wbits):
    try:
        compressed = zlib.compress(data, level=level, wbits=wbits)
        
        # Check output type
        assert isinstance(compressed, bytes)
        
        # Check compression effect based on level
        if level == 0:
            assert compressed == data  # No compression
        elif level > 0:
            assert len(compressed) < len(data)  # Compression occurred
        
    except zlib.error:
        # Check for error on invalid wbits
        assert wbits not in range(9, 16) and wbits not in range(-15, -8) and wbits not in range(25, 32) 
# End program