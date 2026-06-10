from hypothesis import given, strategies as st
import networkx as nx

# ... (graph_strategy as defined above)

@given(graph_strategy, st.integers(0, 9), st.integers(0, 9), st.data())
def test_no_common_ancestor(G, node1, node2, data):
    default_value = data.draw(st.integers())
    lca = nx.lowest_common_ancestor(G, node1, node2, default=default_value)
    if not nx.has_path(G, node1, node2) and not nx.has_path(G, node2, node1):
        assert lca == default_value
# End program 