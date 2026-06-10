from hypothesis import given, strategies as st
import networkx

@given(st.data())
def test_networkx_degree_all_nodes(data):
    G = data.draw(st.graphs(min_size=1)) 
    all_nodes_degree = networkx.degree(G)
    for node in G:
        specific_node_degree = networkx.degree(G, node)
        assert specific_node_degree in [degree for _, degree in all_nodes_degree]
# End program