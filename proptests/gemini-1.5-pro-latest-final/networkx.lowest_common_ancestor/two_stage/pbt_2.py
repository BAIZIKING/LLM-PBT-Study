from hypothesis import given, strategies as st
import networkx as nx

# Define graph generation strategy
def directed_graph_strategy(min_nodes=1, max_nodes=10):
    return st.builds(
        nx.DiGraph,
        st.lists(
            st.tuples(st.integers(min_value=0, max_value=max_nodes-1), 
                      st.integers(min_value=0, max_value=max_nodes-1)),
            min_size=1,
            unique=True
        )
    )

# Define node strategy
def node_strategy(graph):
    return st.sampled_from(list(graph.nodes))

@given(directed_graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_lowest_common_ancestor_property_1(graph, node1, node2):
    lca = nx.lowest_common_ancestor(graph, node1, node2)
    if nx.has_path(graph, node1, node2):
        assert nx.has_path(graph, node1, lca) and nx.has_path(graph, lca, node2)

@given(directed_graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_lowest_common_ancestor_property_2(graph, node1, node2):
    lca = nx.lowest_common_ancestor(graph, node1, node2)
    if nx.has_path(graph, node2, node1):
        assert nx.has_path(graph, node2, lca) and nx.has_path(graph, lca, node1)

@given(directed_graph_strategy(), node_strategy(graph))
def test_networkx_lowest_common_ancestor_property_3(graph, node):
    assert nx.lowest_common_ancestor(graph, node, node) == node

@given(directed_graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_lowest_common_ancestor_property_4(graph, node1, node2):
    lca = nx.lowest_common_ancestor(graph, node1, node2)
    assert nx.lowest_common_ancestor(graph, node1, lca) == lca

@given(directed_graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_lowest_common_ancestor_property_5(graph, node1, node2):
    lca = nx.lowest_common_ancestor(graph, node1, node2)
    assert nx.lowest_common_ancestor(graph, node2, lca) == lca

# End program