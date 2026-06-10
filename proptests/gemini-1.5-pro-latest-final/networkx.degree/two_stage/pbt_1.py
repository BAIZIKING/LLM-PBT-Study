@given(graph_strategy, node_strategy)
def test_degree_equals_weighted_incident_edges(graph, nodes):
    weighted_edges = True
    for (u, v, data) in graph.edges(data=True):
        if 'weight' not in data:
            weighted_edges = False
            break
    if weighted_edges:
        for node in nodes:
            if node in graph:
                assert nx.degree(graph, node, weight='weight') == sum(data['weight'] for u, v, data in graph.edges(node, data=True))
# End program 