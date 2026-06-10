from hypothesis import given, strategies as st
import networkx as nx

# Summary: The generation strategy aims to create a diverse set of inputs for testing `nx.find_cliques`. 
# It generates random graphs with varying sizes and densities, and optionally includes a subset of nodes.

@given(st.data())
def test_networkx_find_cliques(data):
    # Generate a random graph
    num_nodes = data.draw(st.integers(min_value=2, max_value=20))  # Varying graph sizes
    p = data.draw(st.floats(min_value=0.0, max_value=1.0))  # Varying graph densities
    graph = nx.gnp_random_graph(num_nodes, p, seed=data.draw(st.integers()))

    # Optionally generate a subset of nodes
    include_nodes = data.draw(st.booleans())
    if include_nodes:
        num_subset_nodes = data.draw(st.integers(min_value=1, max_value=num_nodes))
        subset_nodes = data.draw(st.lists(st.integers(min_value=0, max_value=num_nodes - 1),
                                          min_size=num_subset_nodes, max_size=num_subset_nodes, unique=True))
    else:
        subset_nodes = None

    # Generate cliques and perform checks
    try:
        cliques = list(nx.find_cliques(graph, nodes=subset_nodes))

        # Property 1: Each clique is a list of nodes
        assert all(isinstance(clique, list) for clique in cliques)
        assert all(isinstance(node, int) for clique in cliques for node in clique)

        # Property 2: Each clique forms a complete subgraph
        for clique in cliques:
            subgraph = graph.subgraph(clique)
            assert nx.is_complete(subgraph)

        # Property 3: (If applicable) Each clique contains all the specified nodes
        if subset_nodes:
            assert all(set(subset_nodes).issubset(clique) for clique in cliques)

    except ValueError:
        # Property 4: If a ValueError is raised, the provided subset of nodes is not a clique
        assert not nx.is_complete(graph.subgraph(subset_nodes))

# End program