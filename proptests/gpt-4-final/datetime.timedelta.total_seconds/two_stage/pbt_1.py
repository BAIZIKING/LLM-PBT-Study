from hypothesis import given, strategies as st
import datetime

@given(st.timedeltas())
def test_type_of_output(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas())
def test_positive_output(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas(min_value=datetime.timedelta(0), max_value=datetime.timedelta(days=365*270)))
def test_accuracy(td1, td2):
    td = td1 + td2
    assert td.total_seconds() == td1.total_seconds() + td2.total_seconds()

@given(st.just(datetime.timedelta(0)))
def test_zero_value(td):
    assert td.total_seconds() == 0.0

@given(st.timedeltas())
def test_idempotence(td):
    total_seconds = td.total_seconds()
    assert total_seconds == td.total_seconds()
# End program