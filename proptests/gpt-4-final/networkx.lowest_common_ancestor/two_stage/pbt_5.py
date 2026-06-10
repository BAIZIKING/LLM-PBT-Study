from hypothesis import given, strategies as st
import networkx as nx

@given(st.graphs(), st.integers(), st.integers(), st.integers())
def test_networkx_lowest_common_ancestor_property(G, node1, node2, default):
    lca = nx.lowest_common_ancestor(G, node1, node2, default)

    # Property 1: The node returned by the function should be a valid node in the graph. Or default if no common ancestor exists.
    assert lca in G.nodes() or lca == default

    # Property 2: If node1 and node2 are the same node, the lowest common ancestor should be that node itself.
    if node1 == node2 and node1 in G.nodes():
        assert lca == node1

    # Property 3: If node1 is an ancestor of node2 or vice versa, then function should return the node that is an ancestor.
    if nx.has_path(G, node1, node2): 
        assert lca == node1
    elif nx.has_path(G, node2, node1): 
        assert lca == node2 

    # Property 4: Function's returned value should be a scalar. It should not be a list or a set.
    assert not isinstance(lca, (list, set))

    # Property 5: If graph does not contain either of the nodes, function should return the default object.
    if node1 not in G.nodes() or node2 not in G.nodes():
        assert lca == default