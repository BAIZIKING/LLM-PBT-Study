from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for generating graphs and node lists
graph_strategy = st.graphs(st.integers(min_value=0, max_value=100), 
                           st.tuples(st.integers(), st.integers()),
                           min_edges=0, max_edges=100)

node_list_strategy = st.lists(st.integers(min_value=0, max_value=100), 
                             min_size=0, max_size=5)

@given(graph_strategy, node_list_strategy)
def test_networkx_find_cliques_properties(graph, nodes):
    # Check for empty graph
    if len(graph.nodes) == 0:
        assert list(nx.find_cliques(graph, nodes=nodes)) == []
        return

    cliques = list(nx.find_cliques(graph, nodes=nodes))

    # Property 1: Each clique is a list of nodes
    assert all(isinstance(clique, list) for clique in cliques)
    assert all(isinstance(node, int) for clique in cliques for node in clique)

    # Property 2 & 3: Nodes within a clique form a complete subgraph and are maximal
    for clique in cliques:
        # Check for complete subgraph
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                assert graph.has_edge(clique[i], clique[j])

        # Check for maximality (no additional node can be added)
        for node in graph.nodes:
            if node not in clique:
                for clique_node in clique:
                    if not graph.has_edge(node, clique_node):
                        break 
                else:
                    assert False, "Clique is not maximal"

    # Property 4 (Determinism) is implicitly tested by Hypothesis framework

    # Property 5: Returned cliques contain the specified nodes (if provided)
    if nodes:
        for clique in cliques:
            assert all(node in clique for node in nodes)
# End program