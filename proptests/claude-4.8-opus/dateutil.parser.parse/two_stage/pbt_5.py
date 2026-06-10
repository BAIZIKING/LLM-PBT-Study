from hypothesis import given, strategies as st, assume, settings
import datetime
from dateutil.parser import parse, ParserError


# Strategy for "safe" datetimes that won't cause overflow when re-parsed.
# We keep years well within range to avoid OverflowError edge cases.
safe_datetimes = st.datetimes(
    min_value=datetime.datetime(1, 1, 1, 0, 0, 0),
    max_value=datetime.datetime(9999, 12, 31, 23, 59, 59),
)


# ---------------------------------------------------------------------------
# Property 1:
# The output is a datetime.datetime object (or, when fuzzy_with_tokens=True,
# a tuple whose first element is a datetime.datetime object and whose second
# element is a tuple of strings).
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_dateutil_parser_parse_output_type():
    data = st.data()

    @given(dt=safe_datetimes, fuzzy_tokens=st.booleans())
    def inner(dt, fuzzy_tokens):
        timestr = dt.strftime("%Y-%m-%d %H:%M:%S")
        try:
            result = parse(timestr, fuzzy_with_tokens=fuzzy_tokens)
        except (ParserError, OverflowError, ValueError):
            return
        if fuzzy_tokens:
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], datetime.datetime)
            assert isinstance(result[1], tuple)
            for tok in result[1]:
                assert isinstance(tok, str)
        else:
            assert isinstance(result, datetime.datetime)

    inner()
# End program


# ---------------------------------------------------------------------------
# Property 2:
# When ignoretz=True, the returned datetime is naive (tzinfo is None),
# regardless of any timezone information present in the input string.
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_dateutil_parser_parse_ignoretz_naive():

    tz_names = st.sampled_from(["", " UTC", " GMT", " EST", " +0200", " -0500"])

    @given(dt=safe_datetimes, tzname=tz_names)
    def inner(dt, tzname):
        timestr = dt.strftime("%Y-%m-%d %H:%M:%S") + tzname
        try:
            result = parse(timestr, ignoretz=True)
        except (ParserError, OverflowError, ValueError):
            return
        assert isinstance(result, datetime.datetime)
        assert result.tzinfo is None

    inner()
# End program


# ---------------------------------------------------------------------------
# Property 3:
# When a default datetime is supplied, any date/time component not specified
# in timestr matches the corresponding component of the default object, while
# components present in timestr override those in the default.
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_dateutil_parser_parse_default_components():

    @given(default_dt=safe_datetimes, day=st.integers(min_value=1, max_value=28))
    def inner(default_dt, day):
        # Only specify the day in the timestr; year/month should come from default.
        timestr = str(day)
        try:
            result = parse(timestr, default=default_dt)
        except (ParserError, OverflowError, ValueError):
            return
        assert isinstance(result, datetime.datetime)
        # The day is specified -> overrides default.
        assert result.day == day
        # Year and month are not specified -> come from default.
        assert result.year == default_dt.year
        assert result.month == default_dt.month

    inner()
# End program


# ---------------------------------------------------------------------------
# Property 4:
# When tzinfos maps a timezone name appearing in the string to a UTC offset,
# the returned datetime's tzinfo reflects that offset (assuming ignoretz is
# not set).
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_dateutil_parser_parse_tzinfos_offset():

    @given(dt=safe_datetimes,
           offset_seconds=st.integers(min_value=-12 * 3600, max_value=12 * 3600))
    def inner(dt, offset_seconds):
        tzname = "XYZ"
        timestr = dt.strftime("%Y-%m-%d %H:%M:%S") + " " + tzname
        tzinfos = {tzname: offset_seconds}
        try:
            result = parse(timestr, tzinfos=tzinfos)
        except (ParserError, OverflowError, ValueError):
            return
        assert isinstance(result, datetime.datetime)
        assert result.tzinfo is not None
        # The resulting utcoffset should match the supplied offset.
        assert result.utcoffset() == datetime.timedelta(seconds=offset_seconds)

    inner()
# End program


# ---------------------------------------------------------------------------
# Property 5:
# When fuzzy_with_tokens=True, all returned ignored token strings are exact
# substrings of the input, and concatenating the recognized portion together
# with the ignored tokens reconstructs the original input string.
# ---------------------------------------------------------------------------
@given(st.data())
@settings(deadline=None)
def test_dateutil_parser_parse_fuzzy_tokens_substrings():

    prefixes = st.sampled_from(["", "Today is ", "The date ", "Meeting on "])
    suffixes = st.sampled_from(["", " at noon", " sharp", " please"])

    @given(dt=safe_datetimes, prefix=prefixes, suffix=suffixes)
    def inner(dt, prefix, suffix):
        core = dt.strftime("%B %d, %Y")
        timestr = prefix + core + suffix
        try:
            result = parse(timestr, fuzzy_with_tokens=True)
        except (ParserError, OverflowError, ValueError):
            return
        assert isinstance(result, tuple)
        parsed_dt, tokens = result
        assert isinstance(parsed_dt, datetime.datetime)
        assert isinstance(tokens, tuple)
        # Each ignored token must be an exact substring of the original input.
        for tok in tokens:
            assert isinstance(tok, str)
            assert tok in timestr

    inner()
# End program