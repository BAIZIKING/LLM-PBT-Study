from hypothesis import given, strategies as st
import pandas as pd
import numpy as np

@given(
    data=st.data(),
    subset=st.lists(st.column_label(), unique=True, max_size=5),
    keep=st.sampled_from(['first', 'last', False]),
    ignore_index=st.booleans()
)
def test_drop_duplicates_properties(data, subset, keep, ignore_index):
    # Generate a DataFrame with random data
    df = data.draw(
        st.dataframe_strategy(
            columns=st.builds(
                pd.DataFrame,
                data=st.lists(
                    st.lists(st.one_of(st.integers(), st.floats(allow_nan=False), st.text()), min_size=1, max_size=10),
                    min_size=1,
                    max_size=10
                )
            ),
            index=st.lists(st.one_of(st.integers(), st.text()), unique=True, min_size=1, max_size=10)
        )
    )

    # Apply drop_duplicates with the given arguments
    result = df.drop_duplicates(subset=subset, keep=keep, ignore_index=ignore_index)

    # Property 1: Output DataFrame should have the same columns as the input DataFrame
    assert set(result.columns) == set(df.columns)

    # Property 2: Output DataFrame should not contain any duplicate rows
    assert result.duplicated(subset=subset).sum() == 0

    # Property 3: If keep='first', output DataFrame should contain the first occurrence of duplicates
    if keep == 'first':
        assert result.equals(df.drop_duplicates(subset=subset, keep='first', ignore_index=ignore_index))

    # Property 4: If keep='last', output DataFrame should contain the last occurrence of duplicates
    if keep == 'last':
        assert result.equals(df.drop_duplicates(subset=subset, keep='last', ignore_index=ignore_index))

    # Property 5: If ignore_index=True, output DataFrame should have a new sequential integer index
    if ignore_index:
        assert result.index.equals(pd.RangeIndex(start=0, stop=len(result), step=1))
# End program