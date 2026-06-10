from hypothesis import given, strategies as st
import datetime

TIMEDELTAS = st.builds(
    datetime.timedelta,
    days=st.integers(min_value=-999_999_999, max_value=999_999_999),
    seconds=st.integers(min_value=0, max_value=86_399),
    microseconds=st.integers(min_value=0, max_value=999_999),
)

SAFE_TOTAL_MICROSECONDS = 4_000_000_000_000_000


@given(st.data())
def test_datetime_timedelta_total_seconds_returns_float(data):
    td = data.draw(TIMEDELTAS)
    assert isinstance(td.total_seconds(), float)


@given(st.data())
def test_datetime_timedelta_total_seconds_equivalent_to_division_by_one_second(data):
    td = data.draw(TIMEDELTAS)

    actual = td.total_seconds()
    expected = td / datetime.timedelta(seconds=1)

    tolerance = max(1e-12, abs(expected) * 1e-15)
    assert abs(actual - expected) <= tolerance


@given(st.data())
def test_datetime_timedelta_total_seconds_matches_normalized_components_formula(data):
    td = data.draw(TIMEDELTAS)

    actual = td.total_seconds()
    expected = td.days * 86_400 + td.seconds + td.microseconds / 1_000_000

    tolerance = max(1e-6, abs(expected) * 1e-15)
    assert abs(actual - expected) <= tolerance


@given(st.data())
def test_datetime_timedelta_total_seconds_sign_matches_timedelta_sign(data):
    td = data.draw(TIMEDELTAS)
    zero = datetime.timedelta(0)

    actual = td.total_seconds()

    if td > zero:
        assert actual > 0.0
    elif td < zero:
        assert actual < 0.0
    else:
        assert actual == 0.0


@given(st.data())
def test_datetime_timedelta_total_seconds_preserves_addition_for_safe_intervals(data):
    microseconds_1 = data.draw(
        st.integers(
            min_value=-SAFE_TOTAL_MICROSECONDS,
            max_value=SAFE_TOTAL_MICROSECONDS,
        )
    )
    microseconds_2 = data.draw(
        st.integers(
            min_value=-SAFE_TOTAL_MICROSECONDS,
            max_value=SAFE_TOTAL_MICROSECONDS,
        )
    )

    td1 = datetime.timedelta(microseconds=microseconds_1)
    td2 = datetime.timedelta(microseconds=microseconds_2)

    actual = (td1 + td2).total_seconds()
    expected = td1.total_seconds() + td2.total_seconds()

    tolerance = max(1e-9, abs(expected) * 1e-15)
    assert abs(actual - expected) <= tolerance


# End program