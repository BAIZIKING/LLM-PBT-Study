from hypothesis import given, strategies as st
import networkx as nx

# Define strategy for generating graphs
graph_strategy = st.builds(nx.fast_gnp_random_graph, st.integers(min_value=1, max_value=50), st.floats(min_value=0, max_value=1))

@given(graph_strategy, st.data())
def test_networkx_lowest_common_ancestor_property(graph, data):
    if nx.is_directed(graph): 
        nodes = list(graph.nodes())
        if len(nodes) < 2:
            return
        node1, node2 = data.draw(st.sampled_from(nodes), st.sampled_from(nodes))

        lca = nx.lowest_common_ancestor(graph, node1, node2, default=None)

        # Test 1: Output should be a node present in the graph
        assert (lca in nodes) or (lca is None)

        if lca is None:
            return

        # Test 2: Output should be an ancestor of both node1 and node2
        assert nx.has_path(graph, lca, node1)
        assert nx.has_path(graph, lca, node2)

        # Test 3: If no common ancestor exists, the output should be the default value
        if not nx.has_path(graph, node1, node2) and not nx.has_path(graph, node2, node1):
            assert lca is None

        # Test 4: If the same node is passed twice (node1 = node2), the output should be the node itself
        if node1 == node2:
            assert lca == node1

        # Test 5: If the graph G consists of only node1 and node2 and they are not connected, the output should be the default value
        if len(nodes) == 2 and not nx.has_path(graph, node1, node2) and not nx.has_path(graph, node2, node1):
            assert lca is None