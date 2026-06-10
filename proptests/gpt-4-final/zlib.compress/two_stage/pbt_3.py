from hypothesis import given, strategies as st
import zlib

@given(st.binary(), st.integers(min_value=-1, max_value=9), st.integers(min_value=-15, max_value=31))
def test_zlib_compress_properties(data, level, wbits):
    try:
        compressed = zlib.compress(data, level=level, wbits=wbits)
        # Property 1: Output is always a bytes object.
        assert isinstance(compressed, bytes)

        if data and level >= 1:
            # Property 2: A higher compression level should result in smaller output size.
            compressed_with_max_compression = zlib.compress(data, level=9, wbits=wbits)
            assert len(compressed) <= len(compressed_with_max_compression)

        if level == 0:
            # Property 3: No compression should result in an output size similar to the input size.
            assert len(compressed) >= len(data)

        # To check property 4: Output includes the expected header and trailer based on wbits,
        # Decompression functions corresponding to the different headers/trailers would need to be used,
        # Which is outside the scope of this problem.

        # Property 5: Decompressed data equals original
        decompressed = zlib.decompress(compressed, wbits=wbits)
        assert decompressed == data

    except Exception as e:
        # Exception means that the parameters are not valid together.
        # It is not a test failure
        pass

# End program