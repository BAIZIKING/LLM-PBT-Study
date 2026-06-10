from hypothesis import given, strategies as st
from datetime import date, timedelta

# Summary: Generate dates from the full supported date range, plus a heavy mix of ISO-calendar edge cases:
# year boundaries, Jan 1/Jan 4/Dec 28/Dec 31 with nearby offsets, min/max dates, leap-year boundaries,
# and documented examples. Check named-tuple shape, weekday numbering, ISO week/year rules, 52/53-week
# constraints, and round-tripping through date.fromisocalendar().
@given(st.data())
def test_datetime_date_isocalendar(data):
    edge_dates = [
        date.min,
        date.max,
        date(2003, 12, 29),
        date(2004, 1, 1),
        date(2004, 1, 4),
        date(2004, 12, 31),
        date(2005, 1, 1),
        date(2009, 12, 31),
        date(2010, 1, 1),
        date(2015, 12, 31),
        date(2016, 1, 1),
        date(2020, 2, 29),
        date(2020, 12, 31),
        date(2021, 1, 1),
    ]

    mode = data.draw(st.sampled_from(["any_date", "fixed_edge", "near_year_boundary"]))

    if mode == "any_date":
        d = data.draw(st.dates(min_value=date.min, max_value=date.max))
    elif mode == "fixed_edge":
        d = data.draw(st.sampled_from(edge_dates))
    else:
        year = data.draw(st.integers(min_value=1, max_value=9999))
        month, day = data.draw(st.sampled_from([(1, 1), (1, 4), (12, 28), (12, 31)]))
        offset = data.draw(st.integers(min_value=-10, max_value=10))
        anchor = date(year, month, day)
        try:
            d = anchor + timedelta(days=offset)
        except OverflowError:
            d = anchor

    iso = d.isocalendar()

    # The result is a named tuple with year, week, and weekday components.
    assert tuple(iso) == (iso.year, iso.week, iso.weekday)
    assert iso[0] == iso.year
    assert iso[1] == iso.week
    assert iso[2] == iso.weekday
    assert iso._fields == ("year", "week", "weekday")

    # ISO weekdays are Monday=1 through Sunday=7.
    expected_weekday = d.weekday() + 1
    assert iso.weekday == expected_weekday
    assert 1 <= iso.weekday <= 7

    # The ISO year is the Gregorian year of the Thursday in the same ISO week.
    thursday = d + timedelta(days=4 - expected_weekday)
    expected_iso_year = thursday.year
    assert iso.year == expected_iso_year

    # Week 1 is the week containing Jan 4, equivalently the first week containing a Thursday.
    jan4 = date(expected_iso_year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    expected_week = ((d - week1_monday).days // 7) + 1
    assert iso.week == expected_week

    # ISO years have either 52 or 53 full weeks.
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def weeks_in_iso_year(year):
        jan1_weekday = date(year, 1, 1).weekday() + 1
        return 53 if jan1_weekday == 4 or (jan1_weekday == 3 and is_leap_year(year)) else 52

    assert weeks_in_iso_year(iso.year) in (52, 53)
    assert 1 <= iso.week <= weeks_in_iso_year(iso.year)

    # The ISO calendar components identify the original Gregorian date.
    assert date.fromisocalendar(iso.year, iso.week, iso.weekday) == d
# End program