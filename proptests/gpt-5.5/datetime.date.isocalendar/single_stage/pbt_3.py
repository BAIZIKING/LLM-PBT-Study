from hypothesis import given, strategies as st
from datetime import date, timedelta

# Summary: Generates dates from the full supported range, with extra focus on ISO edge cases:
# year starts/ends, Jan 4 / Dec 28 ISO anchors, leap days, min/max dates, and documented examples.
# Checks that isocalendar() returns a 3-component named tuple-like object, valid ISO ranges,
# Monday=1..Sunday=7 weekday numbering, the ISO Thursday-year rule, and round-trips through
# date.fromisocalendar().
@given(st.data())
def test_datetime_date_isocalendar(data):
    min_ord = date.min.toordinal()
    max_ord = date.max.toordinal()

    edge_dates = [
        date.min,
        date.max,
        date(2003, 12, 29),
        date(2004, 1, 4),
        date(2004, 1, 1),
        date(2004, 12, 31),
        date(2009, 12, 31),
        date(2010, 1, 1),
        date(2015, 12, 31),
        date(2016, 1, 1),
        date(2020, 2, 29),
        date(1900, 2, 28),
        date(2000, 2, 29),
    ]

    boundary_dates = st.builds(
        lambda y, anchor, offset: date.fromordinal(
            max(min_ord, min(max_ord, date(y, anchor[0], anchor[1]).toordinal() + offset))
        ),
        st.integers(min_value=1, max_value=9999),
        st.sampled_from([(1, 1), (1, 4), (12, 28), (12, 31)]),
        st.integers(min_value=-7, max_value=7),
    )

    d = data.draw(
        st.one_of(
            st.dates(),
            st.sampled_from(edge_dates),
            boundary_dates,
        )
    )

    iso = d.isocalendar()

    assert len(iso) == 3
    assert tuple(iso) == (iso.year, iso.week, iso.weekday)

    year, week, weekday = iso

    assert 1 <= year <= 9999
    assert 1 <= week <= 53
    assert 1 <= weekday <= 7

    assert weekday == d.weekday() + 1

    thursday = d + timedelta(days=4 - weekday)
    assert thursday.weekday() == 3
    assert thursday.year == year

    assert date.fromisocalendar(year, week, weekday) == d

    max_week_for_iso_year = date(year, 12, 28).isocalendar().week
    assert week <= max_week_for_iso_year

# End program