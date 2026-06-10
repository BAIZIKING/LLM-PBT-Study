from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate diverse graphs, node selections, and weight arguments
@given(st.data())
def test_networkx_degree(data):
    # Generate graph
    graph_type = data.draw(st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]))
    graph = data.draw(st.graphs(graph_type))

    # Generate node selection
    nodes = data.draw(
        st.one_of(
            st.sampled_from(list(graph.nodes)),
            st.lists(st.sampled_from(list(graph.nodes) + ["non_existent_node"])),
            st.just([])
        )
    )

    # Generate weight argument
    weight = data.draw(st.one_of(st.none(), st.sampled_from(list(graph.edges(data=True))[0].keys())))

    # Get degree
    degree_view = nx.degree(graph, nodes, weight)

    # Check output type
    assert isinstance(degree_view, dict)

    # Check degree values
    for node, degree in degree_view.items():
        if node not in graph:
            assert degree == 0
        else:
            edges = graph.edges(node, data=True)
            if weight is None:
                assert degree == len(edges)
            else:
                assert degree == sum(data[weight] for _, _, data in edges)

# End program