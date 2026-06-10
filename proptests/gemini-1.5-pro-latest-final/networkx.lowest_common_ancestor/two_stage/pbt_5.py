from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_ancestor_of_both(data):
    G = nx.DiGraph()
    node1 = data.draw(st.integers())
    node2 = data.draw(st.integers())
    common_ancestor = data.draw(st.integers(min_value=min(node1, node2), max_value=max(node1, node2)))
    path_length1 = data.draw(st.integers(min_value=1, max_value=5))  # Limit path length to avoid large graphs
    path_length2 = data.draw(st.integers(min_value=1, max_value=5))  # Limit path length to avoid large graphs
    path1 = list(range(common_ancestor, node1 + 1))
    path2 = list(range(common_ancestor, node2 + 1))
    nx.add_path(G, path1)
    nx.add_path(G, path2)
    lca = nx.lowest_common_ancestor(G, node1, node2) 
    assert nx.has_path(G, lca, node1) and nx.has_path(G, lca, node2)
# End program