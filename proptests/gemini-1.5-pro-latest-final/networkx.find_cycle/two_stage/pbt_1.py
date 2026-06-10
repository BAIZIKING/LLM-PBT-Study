from hypothesis import given, strategies as st
import networkx

# Define strategies for graph generation
def graph_strategy(max_nodes=10, max_edges=20):
    return st.graphs(
        st.integers(min_value=0, max_value=max_nodes-1),
        st.tuples(st.integers(min_value=0, max_value=max_nodes-1), st.integers(min_value=0, max_value=max_nodes-1)),
        max_edges=max_edges
    )

def orientation_strategy():
    return st.sampled_from(['original', 'reverse', 'ignore', None])

# Property 1: Cycle Property
@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_find_cycle_cycle_property(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        assert cycle[0][0] == cycle[-1][-2]  # Check start and end nodes are the same
        for i in range(len(cycle)-1):
            assert cycle[i][-2] == cycle[i+1][0]  # Check consecutive edge connectivity
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

# Property 2: Edge Existence
@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_find_cycle_edge_existence(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        for edge in cycle:
            assert edge[:-1] in graph.edges  # Check if edge exists in the graph 
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

# Property 3: Orientation Consistency (Directed Graphs)
@given(graph=graph_strategy().filter(lambda g: g.is_directed()), orientation=st.just('original'))
def test_find_cycle_orientation_consistency(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        for edge in cycle:
            assert graph.has_edge(*edge[:-1]) and graph.edges[edge[:-1]]['dir'] == edge[-1] 
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

# Property 4: Path Reproduction
@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_find_cycle_path_reproduction(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        current_node = cycle[0][0]
        for edge in cycle:
            assert edge[0] == current_node  # Verify path continuity
            current_node = edge[-2]
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

# Property 5: Uniqueness (Simple Graphs)
@given(graph=graph_strategy().filter(lambda g: not g.is_multigraph()), orientation=orientation_strategy())
def test_find_cycle_uniqueness(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        nodes = [edge[0] for edge in cycle]
        assert len(nodes) == len(set(nodes)) + 1  # One node (start/end) appears twice
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

# End program