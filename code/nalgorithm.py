import networkx as nx

def candidate_node(test_set, grph, algo_type):
    '''Finds most likely candidate node to inherit attributes from

    For each node and its neighbors, identify the most likely node
    to inherit attributes from based on the specified algorithm.

    The following algorithms are supported:
    1. Jaccard Similarity
    2. Adamic/Adar
    3. Preferential Attachment

    .. note:: For Jaccard and Adamic/Adar, if two nodes do not
    share any common neighbors, assign 0.

    :params test_set: target nodes we want to find the most similar neighbor for
    :type test_set: list of str
    :params grph: network graph containing target nodes
    :type grph: networkx.classes.graph.Graph
    :params str alg_type: specification of algorithm type
    :raises: ValueError if algo_type is not included in supported_algorithms
    :returns: node and the most similar neighboring node
    :rtype: dict of {str : str}
    '''

    supported_algorithms = ['jaccard', 'adamic/adar', 'preferential attachment']

    if algo_type not in supported_algorithms:
        raise ValueError('algo_type must be one of the supported algorithms: {}.'.format(supported_algorithms))

    if algo_type == 'jaccard':
        node_selector = nx.jaccard_coefficient
    elif algo_type == 'adamic/adar':
        node_selector = nx.adamic_adar_index
    else:
        node_selector = nx.preferential_attachment

    sim_results = {}

    for i in test_set:
        nearest_neighbors = list(grph.neighbors(i))
        if nearest_neighbors:
            # If a node only has only 1 neighbor, inherit that neighbors attributes
            if len(nearest_neighbors) == 1:
                sim_results[i] = nearest_neighbors[0]
            else:
                # Generate node-neighbor pairings
                node_pairs = [(i, j) for j in nearest_neighbors]

                sim_score = list(node_selector(grph, ebunch=node_pairs))
                sim_score.sort(key=lambda x: x[2], reverse=True)

                sim_results[i] = 0 if sim_score[0][2] == 0 else sim_score[0][1]
        else:
            sim_results[i] = 0

    return sim_results
