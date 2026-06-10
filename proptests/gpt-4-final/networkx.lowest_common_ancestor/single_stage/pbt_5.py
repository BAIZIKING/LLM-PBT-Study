from hypothesis import given, strategies as st
import networkx as nx

@given(st.lists(st.integers(min_value=0, max_value=10), min_size=2, unique=True).flatmap(
    lambda nodes: st.tuples(st.lists(st.tuples(st.sampled_from(nodes), min_size=2, max_size=2), min_size=1), st.sampled_from(nodes), st.sampled_from(nodes))))
def test_lowest_common_ancestor(nodes_and_edges_and_node1_and_node2):
    nodes, edges, node1, node2 = nodes_and_edges_and_node1_and_node2

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    result = nx.lowest_common_ancestor(G, node1, node2)
    
    node1_predecessors = list(nx.ancestors(G, node1))
    node2_predecessors = list(nx.ancestors(G, node2))

    common_ancestors = list(set(node1_predecessors) & set(node2_predecessors))
    if common_ancestors:
        assert result in common_ancestors
    else:
        assert result == None