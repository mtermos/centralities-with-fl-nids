import networkx as nx
import igraph as ig


def _rescale(betweenness, n, normalized, directed=False, k=None, endpoints=False):
    if normalized:
        if endpoints:
            if n < 2:
                scale = None  # no normalization
            else:
                # Scale factor should include endpoint nodes
                scale = 1 / (n * (n - 1))
        elif n <= 2:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / ((n - 1) * (n - 2))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness


def rescale2(dict):
    max_list = []
    for i in dict.values():
        max_list.append(i)
    # Rescaling

    def max_num_in_list(list):
        max = list[0]
        for a in list:
            if a > max:
                max = a
        return max

        # get the factor to divide by max
    max_factor = max_num_in_list(max_list)
    x = {}
    for key, value in dict.items():
        x[key] = value / max_factor
    return x


def cal_betweenness_centrality(G):
    G1 = ig.Graph.from_networkx(G)  # type: ignore
    estimate = G1.betweenness(directed=True)
    # for v in G1.vs:
    #     print(v)
    b = dict(zip(G1.vs["_nx_name"], estimate))
    return _rescale(b, G1.vcount(), True)


def cal_k_core(G):
    G.remove_edges_from(nx.selfloop_edges(G))
    kcore_dict_eachNode = nx.core_number(G)

    kcore_dict_eachNode_normalized = rescale2(kcore_dict_eachNode)

    return kcore_dict_eachNode_normalized


def cal_k_truss(G):
    sr_node_ktruss_dict = {}
    n = G.number_of_nodes()
    G = ig.Graph.from_networkx(G)
    ktrussdict = ktruss(G)
    nodetruss = [0] * n
    for edge in G.es:
        source = edge.source
        target = edge.target
        if not (source == target):
            t = ktrussdict[(source, target)]
        else:
            t = 0
        nodetruss[source] = max(nodetruss[source], t)
        nodetruss[target] = max(nodetruss[target], t)
    d = {}
    node_index = 0
    node_truss_value = 0
    while (node_index < len(nodetruss)):
        d[G.vs[node_index]["_nx_name"]] = nodetruss[node_truss_value]
        node_truss_value = node_truss_value+1
        node_index = node_index+1
    # print(d)
    return rescale2(d)


def edge_support(G):
    nbrs = dict((v.index, set(G.successors(v)) | set(G.predecessors(v)))
                for v in G.vs)
    support = {}
    for e in G.es:
        nod1, nod2 = e.source, e.target
        nod1_nbrs = set(nbrs[nod1])-set([nod1])
        nod2_nbrs = set(nbrs[nod2])-set([nod2])
        sup = len(nod1_nbrs.intersection(nod2_nbrs))
        support[(nod1, nod2)] = sup
    return support


def ktruss(G):
    support = edge_support(G)
    edges = sorted(support, key=support.get)  # type: ignore
    bin_boundaries = [0]
    curr_support = 0
    for i, e in enumerate(edges):
        if support[e] > curr_support:
            bin_boundaries.extend([i]*(support[e]-curr_support))
            curr_support = support[e]

    edge_pos = dict((e, pos) for pos, e in enumerate(edges))

    truss = {}
    neighbors = G.neighborhood()

    nbrs = dict(
        (v.index, (set(neighbors[v.index])-set([v.index]))) for v in G.vs)

    for e in edges:
        u, v = e[0], e[1]
        if not (u == v):
            common_nbrs = set(nbrs[u]).intersection(nbrs[v])
            for w in common_nbrs:
                if (u, w) in support:
                    e1 = (u, w)
                else:
                    e1 = (w, u)
                if (v, w) in support:
                    e2 = (v, w)
                else:
                    e2 = (w, v)
                pos = edge_pos[e1]
                if support[e1] > support[e]:
                    bin_start = bin_boundaries[support[e1]]
                    edge_pos[e1] = bin_start
                    edge_pos[edges[bin_start]] = pos
                    edges[bin_start], edges[pos] = edges[pos], edges[bin_start]
                    bin_boundaries[support[e1]] += 1

                pos = edge_pos[e2]
                if support[e2] > support[e]:
                    bin_start = bin_boundaries[support[e2]]
                    edge_pos[e2] = bin_start
                    edge_pos[edges[bin_start]] = pos
                    edges[bin_start], edges[pos] = edges[pos], edges[bin_start]
                    bin_boundaries[support[e2]] += 1

                support[e1] = max(support[e], support[e1]-1)
                support[e2] = max(support[e], support[e2]-1)

            truss[e] = support[e] + 2
            if v in nbrs[u]:
                nbrs[u].remove(v)
            if u in nbrs[v]:
                nbrs[v].remove(u)
    return truss


def separate_graph(graph, communities):
    """
    Separates a graph into intra-community and inter-community edges.

    Parameters:
    - graph: A NetworkX graph
    - communities: A list of sets, where each set contains the nodes in a community

    Returns:
    - intra_graph: A graph containing only intra-community edges
    - inter_graph: A graph containing only inter-community edges
    """
    # Create new graphs for intra-community and inter-community edges
    intra_graph = nx.Graph()
    inter_graph = nx.Graph()

    # Add all nodes to both graphs to ensure structure is maintained
    intra_graph.add_nodes_from(graph.nodes())
    inter_graph.add_nodes_from(graph.nodes())

    # Organize communities in a way that allows quick lookup of node to community mapping
    node_to_community = {}
    for community_index, community in enumerate(communities):
        for node in community:
            node_to_community[node] = community_index

    # Iterate through each edge in the original graph
    for edge in graph.edges():
        node_u, node_v = edge

        # Determine if an edge is intra-community or inter-community
        if node_to_community.get(node_u) == node_to_community.get(node_v):
            # Intra-community edge
            intra_graph.add_edge(node_u, node_v)
        else:
            # Inter-community edge
            inter_graph.add_edge(node_u, node_v)

    return intra_graph, inter_graph
