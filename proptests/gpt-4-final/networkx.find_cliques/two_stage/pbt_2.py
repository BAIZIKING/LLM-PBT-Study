from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques(data):
    # Generate a random graph
    graph_edge_list = data.draw(st.lists(st.tuples(st.integers(min_value=0, max_value=10),
                                                   st.integers(min_value=0, max_value=10)),
                                         min_size=1, max_size=10))
    G = nx.Graph()
    G.add_edges_from(graph_edge_list)

    # Generate a random set of nodes
    node_list = data.draw(st.lists(st.integers(min_value=0, max_value=10),
                                   min_size=1, max_size=5))

    try:
        cliques = list(nx.find_cliques(G, nodes=node_list))

        # Property 1: Each output from find_cliques is a list of nodes
        assert all(isinstance(clique, list) for clique in cliques)

        # Property 2: If optional list of nodes is provided, each clique should contain all these nodes
        assert all(all(node in clique for node in node_list) for clique in cliques)

        # Property 3: The cliques returned are maximal - no clique should be a proper subset of any other
        for i, clique1 in enumerate(cliques):
            for j, clique2 in enumerate(cliques):
                if i != j:
                    assert not set(clique1).issubset(set(clique2))
        
        # Property 4: The output is an iterable
        try:
            iter(cliques)
        except TypeError:
            assert False

    except ValueError:
        # Property 5: A ValueError is raised if the nodes input is not a clique
        for clique in nx.find_cliques(G):
            if set(node_list).issubset(set(clique)):
                assert False