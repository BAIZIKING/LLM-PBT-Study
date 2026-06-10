from hypothesis import given, strategies as st
from pandas import DataFrame
import numpy as np

@given(st.data())
def test_output_type(data):
    df = DataFrame(data.draw(st.dictionaries(keys=st.text(), values=st.lists(st.integers()))))
    sort_by = data.draw(st.sampled_from(df.columns.tolist()))
    result = df.sort_values(by=sort_by)
    assert isinstance(result, DataFrame) or result is None

@given(st.data())
def test_sorted_order(data):
    df = DataFrame(data.draw(st.dictionaries(keys=st.text(), values=st.lists(st.integers()))))
    sort_by = data.draw(st.sampled_from(df.columns.tolist()))
    result = df.sort_values(by=sort_by)
    assert (result[sort_by].is_monotonic_increasing or result[sort_by].is_monotonic_decreasing)

@given(st.data())
def test_output_content(data):
    df = DataFrame(data.draw(st.dictionaries(keys=st.text(), values=st.lists(st.integers()))))
    sort_by = data.draw(st.sampled_from(df.columns.tolist()))
    result = df.sort_values(by=sort_by)
    assert set(result.columns) == set(df.columns)

@given(st.data())
def test_NaN_position(data):
    df = DataFrame(data.draw(st.dictionaries(keys=st.text(), values=st.lists(st.one_of(st.integers(), st.none())))))
    sort_by = data.draw(st.sampled_from(df.columns.tolist()))
    result = df.sort_values(by=sort_by)
    if result[sort_by].hasnans:
        na_position = np.where(result[sort_by].isna())[0]
        assert (na_position[0] == 0 or na_position[-1] == len(df) - 1)

@given(st.data())
def test_indexing(data):
    df = DataFrame(data.draw(st.dictionaries(keys=st.text(), values=st.lists(st.integers()))))
    sort_by = data.draw(st.sampled_from(df.columns.tolist()))
    result = df.sort_values(by=sort_by, ignore_index=True)
    assert (result.index == range(len(df))).all()