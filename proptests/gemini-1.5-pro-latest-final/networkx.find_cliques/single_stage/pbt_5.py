from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates various graph types/sizes and node lists to test find_cliques comprehensively.
@given(st.data())
def test_networkx_find_cliques(data):
    graph_types = [nx.Graph, nx.DiGraph, nx.MultiGraph]
    graph_type = data.draw(st.sampled_from(graph_types))
    num_nodes = data.draw(st.integers(min_value=0, max_value=100))
    num_edges = data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2))

    # Generate a graph
    G = data.draw(st.graphs(graph_type, num_nodes, num_edges))

    # Generate node list (including edge cases)
    node_list = data.draw(
        st.one_of(
            st.just([]), 
            st.lists(st.integers(min_value=0, max_value=num_nodes - 1), min_size=1, max_size=num_nodes),
            st.just(list(G.nodes))
        )
    )

    # Ensure all nodes in the list exist in the graph
    assert all(node in G for node in node_list)

    try:
        cliques = list(nx.find_cliques(G, nodes=node_list))
        
        for clique in cliques:
            # Check clique definition
            assert all(G.has_edge(u, v) for u in clique for v in clique if u != v)
            
            # Check maximality (no superset is a clique)
            for node in set(G.nodes) - set(clique):
                assert any(not G.has_edge(node, u) for u in clique)
            
            # Check containment (if nodes are specified)
            if node_list:
                assert all(node in clique for node in node_list)
    except ValueError:
        # Ensure ValueError is raised if node_list is not a clique
        if node_list:
            assert any(not G.has_edge(u, v) for u in node_list for v in node_list if u != v) 
        else:
            raise

# End program