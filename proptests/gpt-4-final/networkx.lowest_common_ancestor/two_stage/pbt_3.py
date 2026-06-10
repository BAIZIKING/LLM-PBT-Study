from hypothesis import given, strategies as st
import networkx as nx

# networkx 2.5 does not support generating graphs with hypothesis
# so, we are going to create a small directed graph and our nodes will be positive integers

G = nx.DiGraph()
nx.add_path(G, [0, 1, 2, 3, 4, 5])
nx.add_path(G, [0, 6, 7, 8, 3])

@given(st.integers(min_value=0, max_value=8), st.integers(min_value = 0, max_value=8))
def test_lowest_common_ancestor_property(node1, node2):
    result = nx.lowest_common_ancestor(G, node1, node2)

    # Property 1: The lowest common ancestor should itself be a valid node in G
    assert (result in G.nodes) or (result is None)

    # Property 2 and 3: If node1 and node2 are not in G or do not have a common ancestor, the default value, if provided, is returned
    ancestors1 = nx.ancestors(G, node1) if node1 in G.nodes else set()
    ancestors2 = nx.ancestors(G, node2) if node2 in G.nodes else set()
    if not ancestors1 or not ancestors2 or not ancestors1.intersection(ancestors2):
        assert result is None

    # Property 4: If node1 is an ancestor of node2 or vice-versa, the function should return that node
    if node1 in ancestors2:
        assert result == node1
    if node2 in ancestors1:
        assert result == node2

    # Property 5: The function should return a single node as the LCA
    assert isinstance(result, int) or result is None
# End program