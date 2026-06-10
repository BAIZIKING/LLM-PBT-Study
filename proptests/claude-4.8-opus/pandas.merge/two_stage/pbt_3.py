from hypothesis import given, strategies as st, settings, HealthCheck
import pandas as pd


key_values = st.integers(min_value=0, max_value=20)
payload_values = st.integers(min_value=-1000, max_value=1000)


@st.composite
def df_pair(draw, max_rows=8):
    n_left = draw(st.integers(min_value=0, max_value=max_rows))
    n_right = draw(st.integers(min_value=0, max_value=max_rows))
    left_keys = draw(st.lists(key_values, min_size=n_left, max_size=n_left))
    left_vals = draw(st.lists(payload_values, min_size=n_left, max_size=n_left))
    right_keys = draw(st.lists(key_values, min_size=n_right, max_size=n_right))
    right_vals = draw(st.lists(payload_values, min_size=n_right, max_size=n_right))
    left = pd.DataFrame({"key": left_keys, "lval": left_vals})
    right = pd.DataFrame({"key": right_keys, "rval": right_vals})
    return left, right


# ---------------------------------------------------------------------------
# Property 5: Indicator column correctness
# ---------------------------------------------------------------------------
@given(st.data())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_pandas_merge_indicator_correctness():
    @given(df_pair())
    def inner(pair):
        left, right = pair
        left_keys = set(left["key"].tolist())
        right_keys = set(right["key"].tolist())

        result = pd.merge(left, right, how="outer", on="key", indicator=True)

        # Only the three documented labels may appear.
        assert set(result["_merge"].unique()).issubset(
            {"left_only", "right_only", "both"}
        )

        for _, row in result.iterrows():
            k = row["key"]
            in_left = k in left_keys
            in_right = k in right_keys
            label = row["_merge"]
            if in_left and in_right:
                assert label == "both"
            elif in_left:
                assert label == "left_only"
            else:
                assert label == "right_only"
    inner()
# End program