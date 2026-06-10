from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_drop_duplicates_columns(data):
    # Generate a DataFrame with random data
    df = data.draw(st.data_frames(
        columns=st.lists(st.text(), min_size=1, max_size=5),
        rows=st.lists(st.tuples(st.integers(), st.floats(), st.booleans()), min_size=1, max_size=100)
    ))
    
    result = df.drop_duplicates()
    assert list(result.columns) == list(df.columns)
# End program

@given(st.data())
def test_drop_duplicates_rows(data):
    # Generate a DataFrame with random data
    df = data.draw(st.data_frames(
        columns=st.lists(st.text(), min_size=1, max_size=5),
        rows=st.lists(st.tuples(st.integers(), st.floats(), st.booleans()), min_size=1, max_size=100)
    ))
    
    result = df.drop_duplicates()
    assert len(result) <= len(df)
# End program

@given(st.data())
def test_drop_duplicates_subset(data):
    # Generate a DataFrame with random data
    df = data.draw(st.data_frames(
        columns=st.lists(st.text(), min_size=2, max_size=5),
        rows=st.lists(st.tuples(st.integers(), st.floats(), st.booleans()), min_size=1, max_size=100)
    ))
    
    subset = data.draw(st.lists(st.sampled_from(df.columns), min_size=1, max_size=len(df.columns)-1))
    result = df.drop_duplicates(subset=subset)
    assert result.duplicated(subset=subset).sum() == 0
# End program

@given(st.data())
def test_drop_duplicates_keep_first(data):
    # Generate a DataFrame with random data
    df = data.draw(st.data_frames(
        columns=st.lists(st.text(), min_size=1, max_size=5),
        rows=st.lists(st.tuples(st.integers(), st.floats(), st.booleans()), min_size=1, max_size=100)
    ))
    
    result = df.drop_duplicates(keep='first')
    assert result.equals(df.drop_duplicates())
# End program

@given(st.data())
def test_drop_duplicates_inplace(data):
    # Generate a DataFrame with random data
    df = data.draw(st.data_frames(
        columns=st.lists(st.text(), min_size=1, max_size=5),
        rows=st.lists(st.tuples(st.integers(), st.floats(), st.booleans()), min_size=1, max_size=100)
    ))
    
    original_df = df.copy()
    result = df.drop_duplicates(inplace=True)
    assert result is None
    assert not df.equals(original_df)
# End program