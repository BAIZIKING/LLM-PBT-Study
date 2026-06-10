from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_fromordinal_date_corresponds_to_ordinal(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.toordinal() == ordinal

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_fromordinal_time_components_are_zero(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.hour == 0
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_fromordinal_tzinfo_is_none(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.max.toordinal()))
def test_fromordinal_toordinal_roundtrip(ordinal):
    dt = datetime.datetime.fromordinal(ordinal)
    assert dt.toordinal() == ordinal

@given(st.integers(max_value=0) | st.integers(min_value=datetime.max.toordinal() + 1))
def test_fromordinal_raises_value_error_for_invalid_ordinal(ordinal):
    with pytest.raises(ValueError):
        datetime.datetime.fromordinal(ordinal)
# End program