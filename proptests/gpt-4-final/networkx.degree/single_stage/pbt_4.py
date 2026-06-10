from hypothesis import given, strategies as st
import networkx as nx

@given(st.dictionaries(st.integers(), st.lists(st.integers())), st.one_of(st.integers(), st.lists(st.integers()), st.none()))
def test_networkx_degree(G_dict, nbunch):
    G = nx.Graph(G_dict)
    result = G.degree(nbunch)
    
    # check if result is integer or dictionary
    assert isinstance(result, int) or isinstance(result, dict)

    if isinstance(result, dict):
        # if nbunch is None or omitted, result should contain degrees of all nodes
        if nbunch is None:
            assert len(result) == len(G.nodes)
        else:
            # else result should contain degrees of nodes specified in nbunch
            if isinstance(nbunch, int):
                assert nbunch in result
            else:
                assert all(node in result for node in nbunch)