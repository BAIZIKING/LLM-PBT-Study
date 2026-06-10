from hypothesis import given, strategies as st
import datetime

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR * 365))
def test_fromordinal_output_type(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert isinstance(dt_obj, datetime.datetime)

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR * 365))
def test_fromordinal_time_components(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.hour == 0
    assert dt_obj.minute == 0
    assert dt_obj.second == 0
    assert dt_obj.microsecond == 0

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR * 365))
def test_fromordinal_timezone(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.tzinfo is None

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR * 365))
def test_fromordinal_ordinal_relationship(ordinal):
    dt_obj = datetime.datetime.fromordinal(ordinal)
    assert dt_obj.toordinal() == ordinal

@given(st.integers(min_value=1, max_value=datetime.MAXYEAR * 365),
       st.integers(min_value=1, max_value=datetime.MAXYEAR * 365))
def test_fromordinal_monotonicity(ordinal_1, ordinal_2):
    if ordinal_1 > ordinal_2:
        dt_obj_1 = datetime.datetime.fromordinal(ordinal_1)
        dt_obj_2 = datetime.datetime.fromordinal(ordinal_2)
        assert dt_obj_1 > dt_obj_2
    else:
        # Skip the test if ordinal_1 <= ordinal_2
        pass
# End program