from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for graph generation
graph_types = st.sampled_from([
    nx.empty_graph,
    nx.complete_graph,
    nx.gnp_random_graph,
    nx.star_graph,
    nx.complete_bipartite_graph
])
node_subsets = st.lists(st.integers(), min_size=1)

# Summary: Test that find_cliques returns maximal cliques based on the input graph and node selection.
@given(graph=graph_types, nodes=st.one_of(st.none(), node_subsets))
def test_find_cliques(graph, nodes):
    if nodes is not None:
        # Check if provided nodes form a clique
        if not nx.is_clique(graph, nodes):
            with pytest.raises(ValueError):
                list(nx.find_cliques(graph, nodes))
            return

    cliques = list(nx.find_cliques(graph, nodes))

    for clique in cliques:
        # Verify clique definition (complete subgraph)
        assert nx.is_clique(graph, clique)
        
        # Check maximality (no clique is a subset of another)
        for other_clique in cliques:
            if clique != other_clique:
                assert not set(clique).issubset(set(other_clique))

        # Ensure node presence if specified
        if nodes is not None:
            assert all(node in clique for node in nodes)

# End program