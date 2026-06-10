from hypothesis import given, strategies as st, settings
import networkx as nx

@settings(max_examples=200, deadline=None)
@given(flow_graph=st.builds(nx.DiGraph,
                            edges=st.lists(st.tuples(st.integers(min_value=0, max_value=100),
                                                     st.integers(min_value=0, max_value=100)),
                                           min_size=0, max_size=100, unique=True).map(lambda edges: [(*edge, {'capacity': st.integers(min_value=1, max_value=1000).example()}) for edge in edges])))
def test_flow_value_within_capacity_limits(flow_graph):
    source, target = st.integers(min_value=0, max_value=100).example(), st.integers(min_value=0, max_value=100).example()
    flow_value, _ = nx.maximum_flow(flow_graph, source, target)
    assert 0 <= flow_value <= sum(attr['capacity'] for _, _, attr in flow_graph.out_edges(source, data=True))

@settings(max_examples=200, deadline=None)
@given(flow_graph=st.builds(nx.DiGraph,
                            edges=st.lists(st.tuples(st.integers(min_value=0, max_value=100),
                                                     st.integers(min_value=0, max_value=100)),
                                           min_size=0, max_size=100, unique=True).map(lambda edges: [(*edge, {'capacity': st.integers(min_value=1, max_value=1000).example()}) for edge in edges])))
def test_flow_within_edge_capacity(flow_graph):
    source, target = st.integers(min_value=0, max_value=100).example(), st.integers(min_value=0, max_value=100).example()
    _, flow_dict = nx.maximum_flow(flow_graph, source, target)
    for u, v, attr in flow_graph.edges(data=True):
        assert 0 <= flow_dict[u][v] <= attr['capacity']

@settings(max_examples=200, deadline=None)
@given(flow_graph=st.builds(nx.DiGraph,
                            edges=st.lists(st.tuples(st.integers(min_value=0, max_value=100),
                                                     st.integers(min_value=0, max_value=100)),
                                           min_size=0, max_size=100, unique=True).map(lambda edges: [(*edge, {'capacity': st.integers(min_value=1, max_value=1000).example()}) for edge in edges])))
def test_flow_conservation(flow_graph):
    source, target = st.integers(min_value=0, max_value=100).example(), st.integers(min_value=0, max_value=100).example()
    _, flow_dict = nx.maximum_flow(flow_graph, source, target)
    for node in set(flow_graph.nodes) - {source, target}:
        assert sum(flow_dict[node][v] for v in flow_graph.successors(node)) == sum(flow_dict[u][node] for u in flow_graph.predecessors(node))

@settings(max_examples=50, deadline=None)
@given(flow_graph=st.builds(nx.DiGraph,
                            edges=st.lists(st.tuples(st.integers(min_value=0, max_value=10),
                                                     st.integers(min_value=0, max_value=10)),
                                           min_size=0, max_size=20, unique=True).map(lambda edges: [(*edge, {'capacity': float('inf')}) for edge in edges])))
def test_unbounded_graph_raises_exception(flow_graph):
    source, target = st.integers(min_value=0, max_value=10).example(), st.integers(min_value=0, max_value=10).example()
    try:
        nx.maximum_flow(flow_graph, source, target)
    except nx.NetworkXUnbounded:
        assert True
    else:
        assert False

@settings(max_examples=200, deadline=None)
@given(flow_graph=st.builds(nx.DiGraph,
                            edges=st.lists(st.tuples(st.integers(min_value=0, max_value=100),
                                                     st.integers(min_value=0, max_value=100)),
                                           min_size=0, max_size=100, unique=True).map(lambda edges: [(*edge, {'capacity': st.integers(min_value=1, max_value=1000).example()}) for edge in edges])))
def test_custom_flow_func(flow_graph):
    source, target = st.integers(min_value=0, max_value=100).example(), st.integers(min_value=0, max_value=100).example()
    flow_value, _ = nx.maximum_flow(flow_graph, source, target, flow_func=nx.algorithms.flow.preflow_push)
    assert flow_value == nx.maximum_flow(flow_graph, source, target, flow_func=None)[0]

# End program