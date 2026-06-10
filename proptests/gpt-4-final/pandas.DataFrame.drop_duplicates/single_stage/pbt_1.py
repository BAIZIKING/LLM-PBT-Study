from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

# Generation strategy
@given(
    data=st.data(),
    subset=st.one_of(st.none(), st.text(), st.lists(st.text())),
    keep=st.sampled_from(['first', 'last', False]),
    inplace=st.booleans(),
    ignore_index=st.booleans()
)
def test_pandas_drop_duplicates(data, subset, keep, inplace, ignore_index):
    # Create random dataframe
    num_cols = data.draw(st.integers(min_value=1, max_value=10))
    num_rows = data.draw(st.integers(min_value=1, max_value=50))
    df = pd.DataFrame(
        data=np.random.rand(num_rows, num_cols),
        columns=[f'col_{i}' for i in range(num_cols)]
    )
    # Insert duplicate rows
    if num_rows > 1:
        df = df.append(df.sample(n=num_rows//2), ignore_index=True)

    # Choose subset from columns
    if subset is not None and not isinstance(subset, str):
        max_subset_size = min(num_cols, len(subset))
        if max_subset_size > 0: 
            subset = data.draw(st.lists(subset, max_size=max_subset_size))

    # Drop duplicates
    df_no_duplicates = df.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index)

    # Choose suitable test based on parameters
    if inplace:
        # Check that original dataframe was modified
        assert any(df.duplicated(subset=subset, keep=keep)) == False
    else:
        # Check that a new dataframe was returned and original dataframe was not changed
        assert any(df_no_duplicates.duplicated(subset=subset, keep=keep)) == False
        assert any(df.duplicated(subset=subset, keep=keep)) == True