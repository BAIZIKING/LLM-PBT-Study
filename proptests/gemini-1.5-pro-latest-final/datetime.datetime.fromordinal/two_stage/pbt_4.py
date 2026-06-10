from hypothesis import given, strategies as st
import datetime

# Define a strategy for valid ordinal values, considering potential overflows
max_ordinal = datetime.datetime.max.toordinal()
ordinals = st.integers(min_value=1, max_value=max_ordinal)

@given(ordinals)
def test_output_type(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert isinstance(dt_obj, datetime.datetime)

@given(ordinals)
def test_time_components(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.hour == dt_obj.minute == dt_obj.second == dt_obj.microsecond == 0

@given(ordinals)
def test_timezone(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.tzinfo is None

@given(ordinals)
def test_ordinal_relationship(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.toordinal() == ordinal

@given(ordinals)
def test_date_consistency(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    expected_date = datetime.date.fromordinal(ordinal)
    assert (dt_obj.year, dt_obj.month, dt_obj.day) == (expected_date.year, expected_date.month, expected_date.day)
# End program