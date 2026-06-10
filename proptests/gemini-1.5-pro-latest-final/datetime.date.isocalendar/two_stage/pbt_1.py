from hypothesis import given, strategies as st
import datetime

@given(st.dates())
def test_weekday_range(date):
    weekday = date.isocalendar().weekday
    assert 1 <= weekday <= 7

@given(st.dates())
def test_week_range(date):
    week = date.isocalendar().week
    assert 1 <= week <= 53 

@given(st.dates(month=1, day=1))
def test_first_week_year(date):
    iso_year = date.isocalendar().year
    greg_year = date.year
    assert iso_year == greg_year

@given(st.dates())
def test_next_week(date):
    current_week_date = date.isocalendar()
    next_week_date = (date + datetime.timedelta(days=7)).isocalendar()
    assert next_week_date.week == current_week_date.week + 1 

@given(st.dates(weekday=0)) # 0 represents Monday
def test_monday_week_change(date):
    sunday_week = date.isocalendar().week
    monday_week = (date + datetime.timedelta(days=1)).isocalendar().week
    assert monday_week == sunday_week + 1
# End program