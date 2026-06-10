from hypothesis import given, strategies as st
import networkx


def _draw_flow_graph(data):
    node_count = data.draw(st.integers(min_value=2, max_value=8))
    nodes = list(range(node_count))

    source = data.draw(st.sampled_from(nodes))
    possible_sinks = [node for node in nodes if node != source]
    sink = data.draw(st.sampled_from(possible_sinks))

    capacity_attr = data.draw(st.sampled_from(["capacity", "cap"]))

    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edge_capacities = data.draw(
        st.dictionaries(
            keys=st.sampled_from(possible_edges),
            values=st.integers(min_value=0, max_value=50),
            max_size=len(possible_edges),
        )
    )

    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)
    for (u, v), capacity in edge_capacities.items():
        graph.add_edge(u, v, **{capacity_attr: capacity})

    return graph, source, sink, capacity_attr


def _outgoing_flow(flow_dict, node):
    return sum(flow_dict.get(node, {}).values())


def _incoming_flow(graph, flow_dict, node):
    return sum(flow_dict.get(pred, {}).get(node, 0) for pred in graph.predecessors(node))


def _is_integral(value):
    return value == int(value)


@given(st.data())
def test_networkx_maximum_flow_property(data):
    graph, source, sink, capacity_attr = _draw_flow_graph(data)

    flow_value, flow_dict = networkx.maximum_flow(
        graph,
        source,
        sink,
        capacity=capacity_attr,
    )

    source_net_outflow = _outgoing_flow(flow_dict, source) - _incoming_flow(
        graph, flow_dict, source
    )
    sink_net_inflow = _incoming_flow(graph, flow_dict, sink) - _outgoing_flow(
        flow_dict, sink
    )

    assert flow_value == source_net_outflow
    assert flow_value == sink_net_inflow

    for u, v, attrs in graph.edges(data=True):
        edge_flow = flow_dict[u][v]
        edge_capacity = attrs[capacity_attr]

        assert edge_flow >= 0
        assert edge_flow <= edge_capacity

    for node in graph.nodes:
        if node not in {source, sink}:
            assert _incoming_flow(graph, flow_dict, node) == _outgoing_flow(
                flow_dict, node
            )

    assert flow_value == networkx.maximum_flow_value(
        graph,
        source,
        sink,
        capacity=capacity_attr,
    )

    assert _is_integral(flow_value)
    for u in graph.nodes:
        for v, edge_flow in flow_dict.get(u, {}).items():
            assert _is_integral(edge_flow)


# End program