from hypothesis import given, strategies as st
import pandas as pd

# Summary: Generate DataFrames with various sizes, data types, and duplicate patterns
#         Test different combinations of subset, keep, inplace, and ignore_index parameters
@given(st.data())
def test_pandas_dataframe_drop_duplicates(data):
    # Generate DataFrame
    df_size = data.draw(st.tuples(st.integers(1, 10), st.integers(1, 5)))
    df = pd.DataFrame(data.draw(st.dictionaries(
        keys=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1),
        values=st.one_of(st.integers(), st.floats(), st.text(), st.booleans()),
        min_size=df_size[1], max_size=df_size[1]
    )), index=range(df_size[0]))
    
    # Introduce duplicates
    duplicate_rows = data.draw(st.lists(st.integers(0, df_size[0] - 1), unique=True))
    for row in duplicate_rows:
        df = df.append(df.iloc[row], ignore_index=True)

    # Generate parameters
    subset = data.draw(st.lists(st.sampled_from(df.columns)))
    keep = data.draw(st.sampled_from(['first', 'last', False]))
    inplace = data.draw(st.booleans())
    ignore_index = data.draw(st.booleans())

    original_df = df.copy()  # Keep a copy for comparison

    # Apply drop_duplicates and check properties
    result = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    if inplace:
        assert result is None  # Check for in-place modification
        df_modified = df
    else:
        df_modified = result

    # Check output shape
    expected_num_cols = len(subset) if subset else len(df.columns)
    assert df_modified.shape[1] == expected_num_cols
    if ignore_index:
        assert df_modified.index.equals(pd.Index(range(len(df_modified))))

    # Check duplicate removal logic
    if keep == 'first':
        expected_df = original_df.drop_duplicates(subset=subset, keep='first')
    elif keep == 'last':
        expected_df = original_df.drop_duplicates(subset=subset, keep='last')
    else:
        expected_df = original_df.drop_duplicates(subset=subset)
    assert df_modified.equals(expected_df)

    if not inplace:
        assert original_df.equals(df)  # Check original DataFrame is unchanged
# End program