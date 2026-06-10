from hypothesis import given, strategies as st
import zlib

@given(data=st.text(), wbits=st.integers(-15, 47), bufsize=st.integers())
def test_zlib_decompress(data, wbits, bufsize):
    if wbits < 0:
        # modify the wbits and convert data to bytes
        compressed_data = zlib.compress(data.encode('utf-8'))
    elif wbits > 0:
        # modify the wbits and set the correct header and trailer
        compressed_data = zlib.compress(data.encode('utf-8'))
    else:
        # wbits=0 is only supported since zlib 1.2.3.5
        compressed_data = zlib.compress(data.encode('utf-8'))

    decompressed_data = zlib.decompress(compressed_data, wbits, bufsize)
    
    assert isinstance(decompressed_data, bytes) # The output should be bytes
    assert zlib.decompress(decompressed_data) == data.encode('utf-8') # Decompressing the data again should yield the initial data