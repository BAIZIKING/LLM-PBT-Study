from hypothesis import given, strategies as st
import networkx as nx

# Define a strategy for generating graphs with a reasonable node and edge limit
graph_strategy = st.graphs(
    min_nodes=0, max_nodes=10, min_edges=0, max_edges=20, 
)

# Define a strategy for generating a subset of nodes from a graph
node_subset_strategy = st.builds(
    lambda g: frozenset(st.sampled_from(list(g.nodes))), graph_strategy
)

@given(graph_strategy, node_subset_strategy)
def test_clique_elements_are_nodes(graph, nodes):
    for clique in nx.find_cliques(graph, nodes):
        assert all(node in graph for node in clique) 

@given(graph_strategy, node_subset_strategy)
def test_clique_is_complete(graph, nodes):
    for clique in nx.find_cliques(graph, nodes):
        for n1, n2 in itertools.combinations(clique, 2):
            assert graph.has_edge(n1, n2)

@given(graph_strategy, node_subset_strategy)
def test_clique_is_maximal(graph, nodes):
    for clique in nx.find_cliques(graph, nodes):
        for node in graph:
            if node not in clique:
                assert not all(graph.has_edge(node, c) for c in clique)

@given(graph_strategy, node_subset_strategy)
def test_cliques_contain_specified_nodes(graph, nodes):
    for clique in nx.find_cliques(graph, nodes):
        assert all(n in clique for n in nodes)

@given(graph_strategy)
def test_clique_count_is_reasonable(graph):
    num_cliques = sum(1 for _ in nx.find_cliques(graph))
    num_subgraphs = 2**graph.number_of_edges()  
    assert num_cliques <= num_subgraphs
# End program