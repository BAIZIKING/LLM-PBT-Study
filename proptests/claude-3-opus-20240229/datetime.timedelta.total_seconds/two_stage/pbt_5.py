from hypothesis import given, strategies as st
import datetime

@given(st.timedeltas())
def test_total_seconds_returns_float(td):
    assert isinstance(td.total_seconds(), float)

@given(st.timedeltas())
def test_total_seconds_equals_division(td):
    assert td.total_seconds() == td / datetime.timedelta(seconds=1)

@given(st.timedeltas(min_value=datetime.timedelta(0)))
def test_total_seconds_non_negative(td):
    assert td.total_seconds() >= 0

@given(st.timedeltas(), st.timedeltas())
def test_total_seconds_additive(td1, td2):
    assert (td1 + td2).total_seconds() == td1.total_seconds() + td2.total_seconds()

@given(st.timedeltas(max_value=datetime.timedelta(days=365*270-1)))
def test_total_seconds_large_interval_accuracy(td):
    assert td.total_seconds() == sum(
        microsecond * 1e-6
        for microsecond in (
            td.microseconds,
            td.seconds * 1e6,
            td.days * 24 * 3600 * 1e6,
        )
    )
# End program