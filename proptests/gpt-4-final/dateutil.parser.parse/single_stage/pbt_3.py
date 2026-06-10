import datetime
from hypothesis import given, strategies as st

@given(st.data())
def test_dateutil_parser_parse(data):
    from dateutil.parser import parse
    from dateutil.tz import gettz
    import pytz

    # Generate inputs
    date = data.draw(st.dates())
    time = data.draw(st.times())
    dt_string = f"{date} {time}"

    dayfirst = data.draw(st.booleans())
    yearfirst = data.draw(st.booleans())
    fuzzy = data.draw(st.booleans())
    fuzzy_with_tokens = data.draw(st.booleans())
    ignoretz = data.draw(st.booleans())

    tzinfos = {"CST": gettz("America/Chicago"), "IST": pytz.timezone('Asia/Kolkata')}
    chosen_tzinfo = data.draw(st.sampled_from(list(tzinfos.keys())))

    # Call function
    result = parse(dt_string, dayfirst=dayfirst, yearfirst=yearfirst, 
                   fuzzy=fuzzy, fuzzy_with_tokens=fuzzy_with_tokens,
                   ignoretz=ignoretz, tzinfos=tzinfos)

    
    if fuzzy_with_tokens:
        assert type(result) == tuple
    else:
        assert isinstance(result, datetime.datetime) 
