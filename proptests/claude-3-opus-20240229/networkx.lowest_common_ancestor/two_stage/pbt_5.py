from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_lowest_common_ancestor_properties(data):
    # Generate a random directed graph
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=1, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Property 1: If node1 and node2 are the same node, the function should return that node.
    node = data.draw(st.sampled_from(nodes))
    assert nx.lowest_common_ancestor(G, node, node) == node

    # Property 2: If node1 is an ancestor of node2, the function should return node1.
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nx.descendants(G, node1)))
    assert nx.lowest_common_ancestor(G, node1, node2) == node1

    # Property 3: If node2 is an ancestor of node1, the function should return node2.
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nx.descendants(G, node1)))
    assert nx.lowest_common_ancestor(G, node2, node1) == node2

    # Property 4: If node1 and node2 have no common ancestors and default is None, the function should return None.
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))
    if not nx.has_path(G, node1, node2) and not nx.has_path(G, node2, node1):
        assert nx.lowest_common_ancestor(G, node1, node2) is None

    # Property 5: The returned lowest common ancestor should be an ancestor of both node1 and node2.
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))
    lca = nx.lowest_common_ancestor(G, node1, node2)
    if lca is not None:
        assert nx.has_path(G, lca, node1) and nx.has_path(G, lca, node2)
# End program