from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(st.data())
def test_drop_duplicates_properties(data):
    # Generate input data
    num_rows = data.draw(st.integers(min_value=1, max_value=1000))
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    subset_size = data.draw(st.integers(min_value=0, max_value=num_cols))
    keep_strategy = st.sampled_from(['first', 'last', False])
    ignore_index_strategy = st.booleans()

    column_names = [f'col{i}' for i in range(num_cols)]
    df_data = data.draw(st.lists(st.lists(st.integers(min_value=0, max_value=100), min_size=num_cols, max_size=num_cols), min_size=num_rows, max_size=num_rows))
    
    df = pd.DataFrame(df_data, columns=column_names)
    subset = data.draw(st.lists(st.sampled_from(column_names), min_size=subset_size, max_size=subset_size, unique=True))
    keep = data.draw(keep_strategy)
    ignore_index = data.draw(ignore_index_strategy)

    # Call the function
    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)

    # Property 1: Output DataFrame should have the same columns as input DataFrame
    assert set(result.columns) == set(df.columns)

    # Property 2: Output DataFrame should not contain any duplicate rows based on the specified subset
    if subset:
        assert not result.duplicated(subset=subset).any()
    else:
        assert not result.duplicated().any()

    # Property 3: If keep='first', output should contain the first occurrence of each unique combination
    if keep == 'first':
        expected_result = df.drop_duplicates(subset=subset, keep='first', ignore_index=ignore_index)
        pd.testing.assert_frame_equal(result, expected_result)

    # Property 4: If keep='last', output should contain the last occurrence of each unique combination
    if keep == 'last':
        expected_result = df.drop_duplicates(subset=subset, keep='last', ignore_index=ignore_index)
        pd.testing.assert_frame_equal(result, expected_result)

    # Property 5: If ignore_index=True, output should have a new integer index starting from 0
    if ignore_index:
        assert result.index.equals(pd.RangeIndex(start=0, stop=len(result)))
# End program