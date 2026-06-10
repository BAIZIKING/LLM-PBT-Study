from hypothesis import given, strategies as st
import networkx as nx

@given(st.graphs())
def test_cycle_property(graph):
    try:
        cycle = nx.find_cycle(graph)
        assert cycle[0][0] == cycle[-1][1]
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs())
def test_output_type(graph):
    try:
        cycle = nx.find_cycle(graph)
        assert isinstance(cycle, list)
        for edge in cycle:
            assert isinstance(edge, tuple)
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs())
def test_edge_existence(graph):
    try:
        cycle = nx.find_cycle(graph)
        for edge in cycle:
            assert edge in graph.edges or (edge[1], edge[0]) in graph.edges
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs())
def test_cycle_length(graph):
    try:
        cycle = nx.find_cycle(graph)
        assert len(cycle) >= 3
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs(), st.sampled_from([None, 'original', 'reverse', 'ignore']))
def test_orientation_property(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        if orientation is not None:
            for edge in cycle:
                assert edge[-1] in ['forward', 'reverse']
        else:
            for edge in cycle:
                assert len(edge) == 2 or len(edge) == 3  # For graph or multigraph respectively
    except nx.NetworkXNoCycle:
        pass
# End program