from hypothesis import given, strategies as st
import pandas as pd

@given(st.data())
def test_drop_duplicates_output_columns(data):
    input_data = data.draw(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
    df = pd.DataFrame(input_data, columns=['brand', 'style', 'rating'])
    subset = data.draw(st.none() | st.lists(st.sampled_from(df.columns), max_size=len(df.columns)))
    output_df = df.drop_duplicates(subset=subset)
    assert set(output_df.columns) == set(df.columns)

@given(st.data())
def test_drop_duplicates_no_duplicates(data):
    input_data = data.draw(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
    df = pd.DataFrame(input_data, columns=['brand', 'style', 'rating'])
    subset = data.draw(st.none() | st.lists(st.sampled_from(df.columns), max_size=len(df.columns)))
    output_df = df.drop_duplicates(subset=subset)
    assert output_df.duplicated(subset=subset).sum() == 0

@given(st.data())
def test_drop_duplicates_keep_first(data):
    input_data = data.draw(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
    df = pd.DataFrame(input_data, columns=['brand', 'style', 'rating'])
    subset = data.draw(st.none() | st.lists(st.sampled_from(df.columns), max_size=len(df.columns)))
    output_df = df.drop_duplicates(subset=subset, keep='first')
    assert all(output_df.iloc[0].equals(df.iloc[df.duplicated(subset=subset, keep='first').idxmax()]))

@given(st.data())
def test_drop_duplicates_keep_last(data):
    input_data = data.draw(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
    df = pd.DataFrame(input_data, columns=['brand', 'style', 'rating'])
    subset = data.draw(st.none() | st.lists(st.sampled_from(df.columns), max_size=len(df.columns)))
    output_df = df.drop_duplicates(subset=subset, keep='last')
    assert all(output_df.iloc[-1].equals(df.iloc[df.duplicated(subset=subset, keep='last').idxmax()]))

@given(st.data())
def test_drop_duplicates_ignore_index(data):
    input_data = data.draw(st.lists(st.tuples(st.text(), st.text(), st.floats(allow_nan=False, allow_infinity=False)), min_size=1, max_size=100))
    df = pd.DataFrame(input_data, columns=['brand', 'style', 'rating'])
    subset = data.draw(st.none() | st.lists(st.sampled_from(df.columns), max_size=len(df.columns)))
    output_df = df.drop_duplicates(subset=subset, ignore_index=True)
    assert all(output_df.index == range(len(output_df)))
# End program