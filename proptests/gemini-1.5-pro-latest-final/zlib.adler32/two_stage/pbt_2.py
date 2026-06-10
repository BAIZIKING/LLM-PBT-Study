from hypothesis import given, strategies as st
import zlib

# Define a strategy for generating data, limiting size to avoid excessive runtime
data_strategy = st.binary(max_size=1024)

@given(data=data_strategy, value=st.integers(min_value=0, max_value=2**32-1))
def test_adler32_unsigned_int(data, value):
    checksum = zlib.adler32(data, value)
    assert isinstance(checksum, int) and checksum >= 0 and checksum <= 2**32-1

@given(data=data_strategy, value=st.integers(min_value=0, max_value=2**32-1))
def test_adler32_same_input(data, value):
    checksum1 = zlib.adler32(data, value)
    checksum2 = zlib.adler32(data, value)
    assert checksum1 == checksum2

@given(data=data_strategy, value=st.integers(min_value=0, max_value=2**32-1))
def test_adler32_order_independence(data, value):
    shuffled_data = data[::-1]  # Reverse the data
    checksum1 = zlib.adler32(data, value)
    checksum2 = zlib.adler32(shuffled_data, value)
    assert checksum1 == checksum2

@given(data=data_strategy, value=st.integers(min_value=0, max_value=2**32-1))
def test_adler32_data_change(data, value):
    altered_data = data + b'x'  # Append a byte to change the data
    checksum1 = zlib.adler32(data, value)
    checksum2 = zlib.adler32(altered_data, value)
    assert checksum1 != checksum2

@given(data=data_strategy, value1=st.integers(), value2=st.integers())
def test_adler32_value_change(data, value1, value2):
    if value1 != value2:
        checksum1 = zlib.adler32(data, value1)
        checksum2 = zlib.adler32(data, value2)
        assert checksum1 != checksum2
# End program