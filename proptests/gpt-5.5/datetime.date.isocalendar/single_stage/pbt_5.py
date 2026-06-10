from hypothesis import given, strategies as st
from datetime import date, timedelta

_EDGE_DATES = {
    date.min,
    date.max,
    date(2003, 12, 29),  # documented ISO week/year crossover example
    date(2004, 1, 4),    # documented end of ISO week 1 example
}

for year in [
    1, 2, 3, 4, 5, 6, 7,
    1582, 1600, 1699, 1700,
    1899, 1900, 1999, 2000, 2001,
    2003, 2004, 2005,
    2009, 2010, 2015, 2016, 2020, 2021, 2024,
    9993, 9994, 9995, 9996, 9997, 9998, 9999,
]:
    for day in range(1, 8):
        _EDGE_DATES.add(date(year, 1, day))
    for day in range(25, 32):
        _EDGE_DATES.add(date(year, 12, day))
    try:
        _EDGE_DATES.add(date(year, 2, 29))
    except ValueError:
        pass

_DATE_STRATEGY = st.one_of(
    st.dates(min_value=date.min, max_value=date.max),
    st.sampled_from(sorted(_EDGE_DATES)),
)

# Summary: Generate arbitrary valid datetime.date values across the full supported
# range, while explicitly emphasizing ISO-calendar edge cases: min/max dates,
# Jan/Dec year boundaries, leap days, century/leap-century years, and documented
# dates where Gregorian year and ISO year differ. Check that isocalendar() returns
# a 3-component named-tuple-like result with year/week/weekday fields, that weekday
# uses Monday=1 through Sunday=7, and that ISO year/week match an independent
# calculation based on the Thursday rule and the Monday-starting first ISO week.
@given(st.data())
def test_datetime_date_isocalendar(data):
    d = data.draw(_DATE_STRATEGY, label="date")

    iso = d.isocalendar()

    assert len(iso) == 3
    assert tuple(iso) == (iso.year, iso.week, iso.weekday)

    expected_weekday = d.weekday() + 1
    assert 1 <= iso.weekday <= 7
    assert iso.weekday == expected_weekday

    # The ISO year is the Gregorian year of the Thursday in the same ISO week.
    thursday = d + timedelta(days=4 - expected_weekday)
    expected_year = thursday.year

    # ISO week 1 is the week containing Jan 4, and weeks start on Monday.
    jan4 = date(expected_year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())

    expected_week = ((d - week1_monday).days // 7) + 1

    assert 1 <= iso.week <= 53
    assert iso.year == expected_year
    assert iso.week == expected_week

    current_week_monday = week1_monday + timedelta(weeks=iso.week - 1)
    assert current_week_monday.weekday() == 0
    assert 0 <= (d - current_week_monday).days <= 6

# End program