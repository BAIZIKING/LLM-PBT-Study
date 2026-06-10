from hypothesis import given, strategies as st
import datetime

# Property 1
@given(st.timedeltas())
def test1_timedelta_total_seconds_type(td):
    assert isinstance(td.total_seconds(), float)

# Property 2
@given(st.timedeltas(max_value=datetime.timedelta(days=270*365)))
def test2_timedelta_total_seconds_microsecond_accuracy(td):
    assert (td.total_seconds() * 1000000).is_integer()

# Property 3
@given(st.timedeltas(min_value=datetime.timedelta(days=270*365+1)))
def test3_timedelta_total_seconds_second_accuracy(td):
    assert td.total_seconds() == round(td.total_seconds())

# Property 4
@given(st.just(datetime.timedelta(0)))
def test4_timedelta_total_seconds_zero_duration(td):
    assert td.total_seconds() == 0

# Property 5
@given(st.data())
def test5_timedelta_total_seconds_distribution(data):
    td1 = data.draw(st.timedeltas())
    td2 = data.draw(st.timedeltas())
    assert td1.total_seconds() + td2.total_seconds() == (td1 + td2).total_seconds()
# End program