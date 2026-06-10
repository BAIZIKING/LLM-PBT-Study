from hypothesis import given, strategies as st
import networkx

# Define graph generation strategy with size limitations to avoid overflows
def graph_strategy(max_nodes=100, max_edges=200):
    return st.graphs(
        nodes=st.integers(min_value=1, max_value=max_nodes),
        edges=st.tuples(st.integers(), st.integers()),
        min_edges=1, max_edges=max_edges,
    )

@given(graph_strategy(), st.sampled_from(["original", "ignore", "reverse"]))
def test_cycle_length(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        assert len(cycle) > 2
    except nx.NetworkXNoCycle:
        pass  # No cycle found, property vacuously holds

@given(graph_strategy(), st.sampled_from(["original", "ignore", "reverse"]))
def test_start_end_node(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        start_node, _, *_ = cycle[0]
        end_node, *_ = cycle[-1]
        assert start_node == end_node
    except nx.NetworkXNoCycle:
        pass 

@given(graph_strategy(), st.sampled_from(["original", "ignore", "reverse"]))
def test_unique_edges(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        edge_set = set(cycle)
        assert len(edge_set) == len(cycle)
    except nx.NetworkXNoCycle:
        pass 

@given(graph_strategy(), st.sampled_from(["original", "ignore", "reverse"]))
def test_connectivity(graph, orientation):
    try:
        cycle = nx.find_cycle(graph, orientation=orientation)
        for i in range(len(cycle) - 1):
            u, v, *_ = cycle[i]
            _, w, *_ = cycle[i + 1]
            assert v in graph[u] and v in graph[w]
    except nx.NetworkXNoCycle:
        pass 

@given(st.directed_graphs(graph_strategy()))
def test_orientation_consistency(graph):
    try:
        cycle = nx.find_cycle(graph, orientation="original")
        for u, v, *_ in cycle:
            assert graph.has_edge(u, v)  # Check edge direction
    except nx.NetworkXNoCycle:
        pass 
# End program