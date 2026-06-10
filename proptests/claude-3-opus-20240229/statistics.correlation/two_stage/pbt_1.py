from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays
from math import isclose
import statistics
import numpy as np

@given(st.data())
def test_correlation_range(data):
    x = data.draw(arrays(float, shape=st.integers(min_value=2, max_value=1000)))
    y = data.draw(arrays(float, shape=x.shape))
    assert -1 <= statistics.correlation(x, y) <= 1
    assert -1 <= statistics.correlation(x, y, method='ranked') <= 1

@given(arrays(float, shape=st.integers(min_value=2, max_value=1000)))
def test_correlation_identical(x):
    assert isclose(statistics.correlation(x, x), 1.0)
    assert isclose(statistics.correlation(x, x, method='ranked'), 1.0)

@given(st.data())
def test_correlation_order(data):
    x = data.draw(arrays(float, shape=st.integers(min_value=2, max_value=1000)))
    y = data.draw(arrays(float, shape=x.shape))
    assert isclose(abs(statistics.correlation(x, y)), abs(statistics.correlation(x[::-1], y)))
    assert isclose(abs(statistics.correlation(x, y)), abs(statistics.correlation(x, y[::-1])))
    assert isclose(abs(statistics.correlation(x, y, method='ranked')), abs(statistics.correlation(x[::-1], y, method='ranked')))
    assert isclose(abs(statistics.correlation(x, y, method='ranked')), abs(statistics.correlation(x, y[::-1], method='ranked')))

@given(arrays(float, shape=st.integers(min_value=2, max_value=1000)), st.floats(min_value=-1e10, max_value=1e10))
def test_correlation_scale(x, c):
    assume(c != 0)
    y = x * c
    assert isclose(statistics.correlation(x, y), statistics.correlation(x, x))
    assert isclose(statistics.correlation(x, y, method='ranked'), statistics.correlation(x, x, method='ranked'))

@given(st.floats(min_value=-1e10, max_value=1e10))
def test_correlation_undefined(x):
    with pytest.raises(statistics.StatisticsError):
        statistics.correlation([x, x], [x, x])
    with pytest.raises(statistics.StatisticsError):
        statistics.correlation([x, x], [x, x], method='ranked')
# End program