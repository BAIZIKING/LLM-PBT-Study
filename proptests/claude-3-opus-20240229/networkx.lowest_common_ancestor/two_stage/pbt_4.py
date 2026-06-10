from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_lowest_common_ancestor_properties(data):
    # Generate a random directed graph
    nodes = data.draw(st.lists(st.integers(), unique=True, min_size=2, max_size=100))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True, max_size=1000))
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # Property 1: Returns an ancestor or default value
    node1, node2 = data.draw(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)))
    default_value = data.draw(st.none() | st.integers())
    ancestor = nx.lowest_common_ancestor(G, node1, node2, default=default_value)
    assert ancestor is default_value or nx.has_path(G, ancestor, node1) and nx.has_path(G, ancestor, node2)
    
    # Property 2: If node1 is reachable from node2, then LCA is node2
    if nx.has_path(G, node2, node1):
        assert nx.lowest_common_ancestor(G, node1, node2) == node2
    
    # Property 3: If node2 is reachable from node1, then LCA is node1
    if nx.has_path(G, node1, node2):
        assert nx.lowest_common_ancestor(G, node1, node2) == node1
    
    # Property 4: If node1 and node2 are the same, then LCA is that node
    node = data.draw(st.sampled_from(nodes))
    assert nx.lowest_common_ancestor(G, node, node) == node
    
    # Property 5: No descendant of LCA is also a common ancestor
    ancestor = nx.lowest_common_ancestor(G, node1, node2)
    if ancestor is not None:
        for desc in nx.descendants(G, ancestor):
            assert not (nx.has_path(G, desc, node1) and nx.has_path(G, desc, node2))
# End program