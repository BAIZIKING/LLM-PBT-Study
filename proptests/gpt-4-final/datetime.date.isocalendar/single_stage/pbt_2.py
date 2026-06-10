from hypothesis import given, strategies as st
from datetime import date

@given(st.integers(min_value=1, max_value=9999), st.integers(min_value=1, max_value=12), st.integers(min_value=1, max_value=31))
def test_date_isocalendar(year, month, day):
    try:
        dt = date(year, month, day)
    except ValueError:
        # Invalid date
        return
    else:
        result = dt.isocalendar()
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result.year, int)
        assert isinstance(result.week, int)
        assert isinstance(result.weekday, int)
        assert 1 <= result.year <= 9999
        assert 1 <= result.week <= 53
        assert 1 <= result.weekday <= 7