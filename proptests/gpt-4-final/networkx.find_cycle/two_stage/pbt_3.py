from hypothesis import given, strategies as st
import networkx as nx

@given(st.graphs(), st.integers(min_value=0, max_value=200), st.sampled_from([None, 'original', 'reverse', 'ignore']))
def test_find_cycle(graph, source, orientation):
    try:
        cycle = nx.find_cycle(graph, source=source, orientation=orientation)
        if orientation is not None:
            # Check if direction of traversal ('forward' or 'reverse') is included for each edge
            assert all(len(edge) > 2 for edge in cycle)
        if graph.is_multigraph():
            # Check if the key of the edge is included for multigraphs
            assert all(len(edge) >= 3 for edge in cycle)
    except nx.NetworkXNoCycle:
        # Check if NetworkXNoCycle exception is properly raised when no cycle exists
        assert len(nx.cycle_basis(graph)) == 0
    except nx.NetworkXError:
        # Check if NetworkXError exception is properly raised when source node doesn't exist
        assert not graph.has_node(source)


@given(st.graphs())
def test_find_cycle_unspecified_source(graph):
    try:
        # Test without providing a source parameter
        cycle = nx.find_cycle(graph)
        assert len(cycle) >= 1  # A valid cycle should contain at least one edge
    except nx.NetworkXNoCycle:
        # Check if NetworkXNoCycle exception is properly raised when no cycle exists
        assert len(nx.cycle_basis(graph)) == 0
# End program
