from hypothesis import given, strategies as st
from datetime import date

# Function to generate valid dates
def dates(min_year=1, max_year=9999):
    return st.builds(
        date,
        st.integers(min_value=min_year, max_value=max_year),
        st.integers(min_value=1, max_value=12),
        st.integers(min_value=1, max_value=31),
    ).filter(lambda d: d.year == d.year and d.month == d.month and d.day == d.day)

# Start property-based tests

@given(dates())
def test_return_type(d):
    """Test if the return value is a tuple with three components."""
    icd = d.isocalendar()
    assert isinstance(icd, tuple)
    assert len(icd) == 3

@given(dates())
def test_year_range(d):
    """Test if the output 'year' is within the valid range."""
    icd = d.isocalendar()
    assert 1 <= icd[0] <= 9999

@given(dates())
def test_week_range(d):
    """Test if the output 'week' is within the valid range."""
    icd = d.isocalendar()
    assert 1 <= icd[1] <= 53

@given(dates())
def test_weekday_range(d):
    """Test if the output 'weekday' is within the valid range."""
    icd = d.isocalendar()
    assert 1 <= icd[2] <= 7

@given(dates())
def test_deterministic_behavior(d):
    """Test if the function has deterministic behavior."""
    icd1 = d.isocalendar()
    icd2 = d.isocalendar()
    assert icd1 == icd2

# End program