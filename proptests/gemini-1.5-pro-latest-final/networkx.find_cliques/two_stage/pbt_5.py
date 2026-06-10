from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for generating graphs and node lists
graph_strategy = st.graphs(max_size=10, min_degree=1, max_degree=3)  # Limit size to avoid overflows
node_list_strategy = st.lists(st.integers(), max_size=5)  # Limit size to avoid large inputs

@given(graph_strategy, node_list_strategy)
def test_cliques_are_lists_of_nodes(graph, node_list):
    for clique in nx.find_cliques(graph, nodes=node_list):
        assert isinstance(clique, list)
        assert all(isinstance(node, int) for node in clique)

@given(graph_strategy, node_list_strategy)
def test_cliques_form_complete_subgraphs(graph, node_list):
    for clique in nx.find_cliques(graph, nodes=node_list):
        subgraph = graph.subgraph(clique)
        assert nx.is_complete(subgraph)

@given(graph_strategy) 
def test_cliques_are_maximal(graph):
    for clique in nx.find_cliques(graph):
        for node in graph.nodes:
            if node not in clique:
                subgraph = graph.subgraph(clique + [node])
                assert not nx.is_complete(subgraph) 

@given(graph_strategy)
def test_finds_all_maximal_cliques(graph):
    found_cliques = set(tuple(sorted(c)) for c in nx.find_cliques(graph))
    for node_set in nx.powerset(graph.nodes):
        if len(node_set) > 1 and nx.is_complete(graph.subgraph(node_set)):
            assert tuple(sorted(node_set)) in found_cliques

@given(graph_strategy, node_list_strategy)
def test_node_filtering(graph, node_list):
    try:
        for clique in nx.find_cliques(graph, nodes=node_list):
            assert all(node in clique for node in node_list)
    except ValueError:
        assert not nx.is_complete(graph.subgraph(node_list))  # Ensure ValueError is raised only when nodes is not a clique

# End program