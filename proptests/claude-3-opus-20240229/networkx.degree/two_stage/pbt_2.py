from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_degree_view_length(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=1000))
    G = nx.gnm_random_graph(num_nodes, data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2)))
    nbunch = data.draw(st.none() | st.lists(st.integers(min_value=0, max_value=num_nodes-1), min_size=1, max_size=num_nodes, unique=True))
    degree_view = nx.degree(G, nbunch)
    if nbunch is None:
        assert len(degree_view) == len(G)
    else:
        assert len(degree_view) == len(nbunch)

@given(st.data())
def test_degree_values_non_negative(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=1000))
    G = nx.gnm_random_graph(num_nodes, data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2)))
    nbunch = data.draw(st.none() | st.lists(st.integers(min_value=0, max_value=num_nodes-1), min_size=1, max_size=num_nodes, unique=True))
    degree_view = nx.degree(G, nbunch)
    assert all(deg >= 0 for _, deg in degree_view)

@given(st.data())
def test_degree_sum_twice_num_edges(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=1000))
    G = nx.gnm_random_graph(num_nodes, data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2)))
    degree_view = nx.degree(G)
    assert sum(deg for _, deg in degree_view) == 2 * len(G.edges)

@given(st.data())
def test_degree_single_node(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=1000))
    G = nx.gnm_random_graph(num_nodes, data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2)))
    node = data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    degree_view = nx.degree(G, [node])
    assert len(degree_view) == 1
    assert degree_view[node] == G.degree(node)

@given(st.data())
def test_degree_undirected_graph(data):
    num_nodes = data.draw(st.integers(min_value=1, max_value=1000))
    G = nx.gnm_random_graph(num_nodes, data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2)))
    degree_view = nx.degree(G)
    for node, deg in degree_view:
        assert deg >= len(list(G.edges(node)))
# End program