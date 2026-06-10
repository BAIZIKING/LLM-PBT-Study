from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_datetime_fromordinal_type(ordinal):
    dt_object = datetime.datetime.fromordinal(ordinal)
    assert type(dt_object) == datetime.datetime

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_datetime_fromordinal_time_components(ordinal):
    dt_object = datetime.datetime.fromordinal(ordinal)
    assert dt_object.hour == 0
    assert dt_object.minute == 0
    assert dt_object.second == 0
    assert dt_object.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_datetime_fromordinal_tzinfo(ordinal):
    dt_object = datetime.datetime.fromordinal(ordinal)
    assert dt_object.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal()))
def test_datetime_datetime_fromordinal_inverse(ordinal):
    dt_object = datetime.datetime.fromordinal(ordinal)
    assert dt_object.toordinal() == ordinal

@given(st.integers(min_value=1, max_value=datetime.datetime.max.toordinal() - 1))
def test_datetime_datetime_fromordinal_successive_days(ordinal):
    dt_object1 = datetime.datetime.fromordinal(ordinal)
    dt_object2 = datetime.datetime.fromordinal(ordinal + 1)
    difference = dt_object2 - dt_object1
    assert difference.days == 1
# End program