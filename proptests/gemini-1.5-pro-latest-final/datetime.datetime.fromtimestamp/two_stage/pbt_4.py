from hypothesis import given, strategies as st
import datetime

# Define a strategy for generating timestamps within a reasonable range
timestamps = st.integers(min_value=0, max_value=253402300799)  # Max value represents Dec 31, 9999

# Define a strategy for generating optional time zone information
tzinfo_strategy = st.one_of(st.none(), st.builds(datetime.timezone.utc))

@given(timestamps, tzinfo_strategy)
def test_datetime_fromtimestamp_type(timestamp, tz):
    """Output Type: The output of the function is always a datetime object."""
    result = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert isinstance(result, datetime.datetime)

@given(timestamps, tzinfo_strategy)
def test_datetime_fromtimestamp_timezone(timestamp, tz):
    """Time Zone: Time zone is handled correctly based on the 'tz' argument."""
    result = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    if tz is None:
        assert result.tzinfo is None  # Naive datetime object
    else:
        assert result.tzinfo == tz  # Aware datetime object with specified time zone

@given(st.integers())  # Generate timestamps without restrictions for overflow testing
def test_datetime_fromtimestamp_overflow(timestamp):
    """Timestamp Range: OverflowError is raised for out-of-range timestamps."""
    with pytest.raises(OverflowError):
        datetime.datetime.fromtimestamp(timestamp)

@given(st.lists(timestamps, min_size=2, unique=True).flatmap(
    lambda l: st.tuples(st.just(l), st.permutations(l))))
def test_datetime_fromtimestamp_monotonicity(data):
    """Monotonicity: Increasing timestamps result in increasing datetime objects."""
    timestamps, permutation = data
    datetimes = [datetime.datetime.fromtimestamp(ts) for ts in permutation]
    for i in range(1, len(datetimes)):
        assert datetimes[i - 1] <= datetimes[i]

@given(timestamps, tzinfo_strategy)
def test_datetime_fromtimestamp_uniqueness(timestamp, tz):
    """Uniqueness: Distinct timestamps result in distinct datetime objects."""
    dt1 = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    dt2 = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    assert dt1 == dt2

# End program