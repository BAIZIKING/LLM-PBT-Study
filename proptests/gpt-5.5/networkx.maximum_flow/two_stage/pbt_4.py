from hypothesis import given, strategies as st
import networkx

@given(st.data())
def test_networkx_maximum_flow_property(data):
    n = data.draw(st.integers(min_value=2, max_value=8))
    nodes = list(range(n))

    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([node for node in nodes if node != source]))

    unordered_pairs = [(u, v) for u in nodes for v in nodes if u < v]
    selected_pairs = data.draw(
        st.lists(
            st.sampled_from(unordered_pairs),
            unique=True,
            max_size=len(unordered_pairs),
        )
    )

    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)

    for u, v in selected_pairs:
        capacity = data.draw(st.integers(min_value=0, max_value=20))
        if data.draw(st.booleans()):
            graph.add_edge(u, v, capacity=capacity)
        else:
            graph.add_edge(v, u, capacity=capacity)

    flow_value, flow_dict = networkx.maximum_flow(graph, source, sink)

    for u, v, edge_data in graph.edges(data=True):
        capacity = edge_data["capacity"]
        edge_flow = flow_dict[u][v]
        assert 0 <= edge_flow <= capacity

    for node in graph.nodes:
        incoming_flow = sum(flow_dict[pred][node] for pred in graph.predecessors(node))
        outgoing_flow = sum(flow_dict[node][succ] for succ in graph.successors(node))

        if node not in {source, sink}:
            assert incoming_flow == outgoing_flow

    source_outgoing = sum(flow_dict[source][succ] for succ in graph.successors(source))
    source_incoming = sum(flow_dict[pred][source] for pred in graph.predecessors(source))
    assert flow_value == source_outgoing - source_incoming

    sink_incoming = sum(flow_dict[pred][sink] for pred in graph.predecessors(sink))
    sink_outgoing = sum(flow_dict[sink][succ] for succ in graph.successors(sink))
    assert flow_value == sink_incoming - sink_outgoing

    reachable = {source}
    stack = [source]

    while stack:
        u = stack.pop()

        for v in graph.successors(u):
            residual_capacity = graph[u][v]["capacity"] - flow_dict[u][v]
            if residual_capacity > 0 and v not in reachable:
                reachable.add(v)
                stack.append(v)

        for v in graph.predecessors(u):
            residual_capacity = flow_dict[v][u]
            if residual_capacity > 0 and v not in reachable:
                reachable.add(v)
                stack.append(v)

    assert sink not in reachable

    cut_capacity = sum(
        graph[u][v]["capacity"]
        for u in reachable
        for v in graph.successors(u)
        if v not in reachable
    )
    assert flow_value == cut_capacity

# End program