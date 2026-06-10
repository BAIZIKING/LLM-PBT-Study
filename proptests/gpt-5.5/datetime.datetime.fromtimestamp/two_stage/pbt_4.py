from hypothesis import given, strategies as st
import datetime


safe_timestamps = st.floats(
    min_value=0,
    max_value=2_000_000_000,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

safe_integer_timestamps = st.integers(
    min_value=0,
    max_value=2_000_000_000,
)

timezones = st.integers(min_value=-1439, max_value=1439).map(
    lambda minutes: datetime.timezone(datetime.timedelta(minutes=minutes))
)


@given(st.data())
def test_datetime_datetime_fromtimestamp_returns_datetime_instance(data):
    timestamp = data.draw(safe_timestamps)

    result = datetime.datetime.fromtimestamp(timestamp)

    assert isinstance(result, datetime.datetime)


@given(st.data())
def test_datetime_datetime_fromtimestamp_without_tz_returns_naive_datetime(data):
    timestamp = data.draw(safe_timestamps)

    result = datetime.datetime.fromtimestamp(timestamp)

    assert result.tzinfo is None


@given(st.data())
def test_datetime_datetime_fromtimestamp_with_tz_round_trips_timestamp(data):
    timestamp = data.draw(safe_timestamps)
    tz = data.draw(timezones)

    result = datetime.datetime.fromtimestamp(timestamp, tz=tz)

    assert result.tzinfo is tz
    assert abs(result.timestamp() - timestamp) <= max(1e-6, abs(timestamp) * 1e-15)


@given(st.data())
def test_datetime_datetime_fromtimestamp_utc_matches_epoch_plus_seconds(data):
    timestamp = data.draw(safe_integer_timestamps)

    result = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    expected = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
        seconds=timestamp
    )

    assert result == expected


@given(st.data())
def test_datetime_datetime_fromtimestamp_has_valid_fields_and_fold(data):
    timestamp = data.draw(safe_timestamps)
    tz = data.draw(st.one_of(st.none(), timezones))

    result = datetime.datetime.fromtimestamp(timestamp, tz=tz)

    assert 1 <= result.month <= 12
    assert 1 <= result.day <= 31
    assert 0 <= result.hour <= 23
    assert 0 <= result.minute <= 59
    assert 0 <= result.second <= 59
    assert 0 <= result.microsecond <= 999999
    assert result.fold in (0, 1)


# End program