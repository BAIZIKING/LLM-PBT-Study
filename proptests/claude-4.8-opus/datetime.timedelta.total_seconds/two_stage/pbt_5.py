from hypothesis import given, strategies as st
import datetime
import math

# Strategy for timedeltas. We bound the days to avoid the documented loss of
# microsecond accuracy (which occurs beyond ~270 years) and to keep arithmetic
# from overflowing timedelta's own internal limits.
# timedelta.max is roughly 999999999 days; we stay well within ~250 years
# (~91250 days) so microsecond accuracy is preserved for the additive tests.
safe_td = st.timedeltas(
    min_value=datetime.timedelta(days=-91250),
    max_value=datetime.timedelta(days=91250),
)


@given(td=safe_td)
def test_total_seconds_returns_float(td):
    # Property 1: output is always a float.
    result = td.total_seconds()
    assert isinstance(result, float)
# End program


@given(td=safe_td)
def test_total_seconds_equals_division_form(td):
    # Property 2: equals td / timedelta(seconds=1).
    assert td.total_seconds() == td / datetime.timedelta(seconds=1)
# End program


@given(td=safe_td)
def test_total_seconds_sign_matches_duration(td):
    # Property 3: sign of output matches sign of duration.
    result = td.total_seconds()
    zero = datetime.timedelta(0)
    if td > zero:
        assert result > 0
    elif td < zero:
        assert result < 0
    else:
        assert result == 0.0
# End program


@given(td=safe_td)
def test_total_seconds_component_breakdown(td):
    # Property 4: equals days*86400 + seconds + microseconds/1_000_000.
    expected = td.days * 86400 + td.seconds + td.microseconds / 1_000_000
    assert math.isclose(td.total_seconds(), expected, rel_tol=1e-9, abs_tol=1e-6)
# End program


@given(a=safe_td, b=safe_td, k=st.integers(min_value=-1000, max_value=1000))
def test_total_seconds_linearity(a, b, k):
    # Property 5: additivity and scalar multiplication (within timedelta limits).
    sum_td = a + b
    assert math.isclose(
        sum_td.total_seconds(),
        a.total_seconds() + b.total_seconds(),
        rel_tol=1e-9,
        abs_tol=1e-6,
    )
    scaled = k * a
    assert math.isclose(
        scaled.total_seconds(),
        k * a.total_seconds(),
        rel_tol=1e-9,
        abs_tol=1e-6,
    )
# End program