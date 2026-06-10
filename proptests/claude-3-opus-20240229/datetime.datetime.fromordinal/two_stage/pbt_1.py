from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_same_ordinal(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.toordinal() == ordinal

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_zero_time_components(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_fromordinal_none_tzinfo(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.tzinfo is None

@given(st.integers(max_value=0))
def test_fromordinal_raises_value_error_for_ordinal_less_than_one(ordinal):
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(ordinal)

@given(st.integers(min_value=datetime.datetime.max.toordinal() + 1))
def test_fromordinal_raises_value_error_for_ordinal_greater_than_max(ordinal):
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(ordinal)
# End program