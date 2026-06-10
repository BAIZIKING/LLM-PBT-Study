from hypothesis import given, strategies as st
import networkx as nx

# Define a strategy for generating graphs with a limited number of nodes and edges
# to avoid performance issues with large graphs. 
graph_strategy = st.builds(
    nx.Graph,
    st.lists(st.integers(min_value=0, max_value=100), max_size=10),
    st.lists(st.tuples(st.integers(min_value=0, max_value=100), st.integers(min_value=0, max_value=100)), max_size=20),
)

# Define a strategy for generating lists of nodes within the generated graphs.
node_list_strategy = st.builds(
    lambda g: st.lists(st.sampled_from(g.nodes), max_size=5),
    graph_strategy,
)


@given(graph_strategy)
def test_cliques_are_subsets_of_graph(graph):
    """Tests that all cliques found are subsets of the graph's nodes."""
    for clique in nx.find_cliques(graph):
        assert set(clique).issubset(graph.nodes)


@given(graph_strategy)
def test_cliques_are_complete_subgraphs(graph):
    """Tests that each clique forms a complete subgraph."""
    for clique in nx.find_cliques(graph):
        subgraph = graph.subgraph(clique)
        assert nx.is_complete(subgraph)


@given(graph_strategy)
def test_clique_for_every_node(graph):
    """Tests that every node is present in at least one found clique."""
    all_nodes_in_cliques = set()
    for clique in nx.find_cliques(graph):
        all_nodes_in_cliques.update(clique)
    assert all_nodes_in_cliques == set(graph.nodes)


@given(graph_strategy, node_list_strategy)
def test_cliques_contain_given_nodes(graph, node_list):
    """Tests that if a node list is provided, all returned cliques are supersets of it."""
    if not nx.is_clique(graph, node_list):
        with pytest.raises(ValueError):
            list(nx.find_cliques(graph, node_list))
    else:
        for clique in nx.find_cliques(graph, node_list):
            assert set(node_list).issubset(clique)


@given(graph_strategy)
def test_all_nodes_in_cliques(graph):
    """Tests that the set of all nodes in cliques equals the set of graph nodes."""
    clique_nodes = set()
    for clique in nx.find_cliques(graph):
        clique_nodes.update(clique)
    assert clique_nodes == set(graph.nodes)

# End program