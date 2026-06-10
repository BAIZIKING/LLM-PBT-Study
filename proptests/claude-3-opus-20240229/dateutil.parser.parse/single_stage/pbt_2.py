from hypothesis import given, strategies as st
from dateutil.parser import parse
from dateutil.tz import gettz
import datetime

# Summary: 
# Generate a wide variety of string formats that are valid and invalid
# to test parsing robustness. Include ambiguous formats to test the 
# dayfirst and yearfirst options. Generate time zone names and offsets 
# to test the tzinfos option. Use the default option to check element
# replacement. Set ignoretz and fuzzy options.
# Check the return type is datetime or a tuple if fuzzy_with_tokens=True.
# Check elements are replaced correctly when a default is given.
# Check time zones are handled properly based on ignoretz and tzinfos.
# Check ParserError is raised for invalid strings.

@given(st.data())
def test_dateutil_parser_parse(data):
    # Generate valid datestring formats
    timestr = data.draw(st.one_of(
        st.dates().map(lambda d: d.strftime('%Y-%m-%d')),
        st.times().map(lambda t: t.strftime('%H:%M:%S')), 
        st.datetimes().map(lambda dt: dt.isoformat()),
    ))
    
    # Generate invalid formats
    invalid_timestr = data.draw(st.text())

    # Generate replaceable default datetime
    default_dt = data.draw(st.datetimes())

    # Generate tzinfo dicts
    tznames = ('UTC', 'CST', 'BRST', 'GMT', data.draw(st.text(max_size=8)))
    offsets = (None, 0, -7200, data.draw(st.integers(min_value=-86400, max_value=86400)))
    tzinfos = {name:offset for name,offset in zip(tznames, offsets) if offset is not None}
    tzinfos[data.draw(st.sampled_from(tznames))] = gettz(data.draw(st.timezones()))

    # Generate options
    dayfirst = data.draw(st.booleans()) 
    yearfirst = data.draw(st.booleans())
    fuzzy = data.draw(st.booleans())
    fuzzy_with_tokens = data.draw(st.booleans())
    ignoretz = data.draw(st.booleans())

    # Parse valid timestr
    dt = parse(timestr, default=default_dt, dayfirst=dayfirst, yearfirst=yearfirst,
               fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens, 
               ignoretz=ignoretz, tzinfos=tzinfos)

    # Check return types
    if fuzzy_with_tokens:
        assert isinstance(dt, tuple)
        assert isinstance(dt[0], datetime.datetime)
        assert isinstance(dt[1], tuple) and all(isinstance(e, str) for e in dt[1])
    else:
        assert isinstance(dt, datetime.datetime)

    # Check default replacement
    assert dt.replace(hour=default_dt.hour, minute=default_dt.minute) == dt

    # Check dayfirst/yearfirst
    if len(timestr.split('-')) == 3:  # check only unambiguous date formats
        if dayfirst:
            assert dt.day == int(timestr.split('-')[0])
        if yearfirst:
            assert dt.year == int(timestr.split('-')[0])

    # Check timezone handling  
    if not ignoretz:
        for name,offset in tzinfos.items():
            if isinstance(offset, int):
                if timestr.endswith(name):
                    assert dt.utcoffset().total_seconds() == offset
            elif isinstance(offset, datetime.tzinfo):
                if timestr.endswith(name):
                    assert dt.tzinfo == offset

    # Check invalid timestr raises error
    try:
        parse(invalid_timestr)
    except ValueError:
        pass  # expected
    else:
        assert False, "ParserError not raised"
# End program