from hypothesis import given, strategies as st
import statistics

@given(st.lists(st.integers(), min_size=5, unique=True))
def test_median_iqr(data):
    data.sort()
    q1 = statistics.median(data[:len(data)//2])
    q3 = statistics.median(data[len(data)//2:])
    iqr = q3 - q1
    
    # Add/remove values outside IQR
    data_modified = data + [q1 - 2*iqr, q3 + 2*iqr]
    assert statistics.median(data) == statistics.median(data_modified)
# End program