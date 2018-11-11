# Import Libraries
import pandas as pd
import numpy as np
import networkx as nx
import time
import sys
import unittest

# The following function adj_list_to_file is taken and modified from
# stack overflow: https://stackoverflow.com/questions/34917550/write
# -a-graph-into-a-file-in-an-adjacency-list-form-mentioning-all-
# neighbors-of
def adj_list_to_file(G, file_name):
    '''Create adjacency list and save as text file

    :params G: network graph
    :type G: networkx graph
    :params file_name: file name and save location
    :type file_name: str
    '''

    with open(file_name, "w") as f:
        for n in G.nodes():
            f.write(str(n) + ',')
            for neighbor in G.neighbors(n):
                f.write(str(neighbor) + ' ')
            f.write('\n')


def save_candidate_pairs(c_pairs, file_name):
    '''Save candidate pairs as csv file

    :params c_pairs: candidate node pairs
    :type c_pairs: nested list
    :params file_name: file name and save location
    :type file_name: str
    '''

    with open(file_name, "w") as f:
        f.write('node1,node2,CN\n')
        for i in c_pairs:
            f.write('{}, {}, {}\n'.format(i[0][0], i[0][1], i[1]))


# The following 5 functions (filter_by_lemma1, invert_adjacency_list,
# generate_accompanied_groups, filter_by_lemma2, generate_node_pairs)
# were created using the following paper as a reference:
#
# Cui W, Pu C, Xu Z, Cai S, Yang J, Michaelson A. Bounded link
# prediction in very large networks. Physics A: Statistical Mechanics
# and its Applications. 2016;457:202-214. doi:https://doi.org/10.101
# 6/j.physa.2016.03.041.

def filter_by_lemma1(adj_list, L):
    '''Filter nodes with neighbors less than or equal to L

    If the number of their neighbors is no greater than threshold L,
    these pairs will not have more than L common neighbors.

    For example, the following is an adjacency list represented as a
    python dictionary. The key is a node, and the value is a list of
    common neighbors.

    {0: [1, 2, 4, 5, 7],
     1: [0, 2, 4, 7],
     2: [0, 1, 3, 5, 6],
     3: [2, 4, 6, 7],
     4: [0, 1, 3, 6],
     5: [0, 2],
     6: [2, 3, 4],
     7: [0, 1, 3]}

    Setting L to 3, this function will filter out nodes that have
    3 or less neighbors. The resulting nodes will be the following:

    {0: [1, 2, 4, 5, 7],
     1: [0, 2, 4, 7],
     2: [0, 1, 3, 5, 6],
     3: [2, 4, 6, 7],
     4: [0, 1, 3, 6]}

    :param adj_list: adjacency list
    :type adj_list: dict
    :param L: threshold for common neighbors
    :type L: int
    :return: adjacency list containing nodes with more than L neighbors
    :rtype: dict
    '''

    adj_new = {}

    for k, v in adj_list.items():
        if len(v) > L:
            adj_new[k] = v

    return adj_new


def invert_adjacency_list(adj_list):
    '''Invert the adjacency matrix.

    For example, the following is an adjacency list represented as a
    python dictionary. The key is a node, and the value is a list of
    common neighbors of that node.

    {0: [1, 2, 4, 5, 7],
     1: [0, 2, 4, 7],
     2: [0, 1, 3, 5, 6],
     3: [2, 4, 6, 7],
     4: [0, 1, 3, 6]}

    Starting with node 1, we see that it appears in the adjacency
    list of node 0, 2, and 4. Thus, the inverted representation will
    be '1: [0, 2, 4]'. The resulting inverted adjaceny list will be
    the following:

    {0: [1, 2, 4],
     1: [0, 2, 4],
     2: [0, 1, 3],
     3: [2, 4],
     4: [0, 1, 3],
     5: [0, 2],
     6: [2, 3, 4],
     7: [0, 1, 3]}

    :param adj_list: adjacency list
    :type adj_list: dict
    :return: inverted adjacency list
    :rtype: dict
    '''

    adj_inv = {}

    for k, v in adj_list.items():
        for i in v:
            if i in adj_inv:
                adj_inv[i].append(k)
            else:
                adj_inv[i] = [k]

    return adj_inv


def generate_accompanied_groups(adj_list):
    '''Generate accompanying groups in (address, size) representation

    For example, node 4 is present in the adjacency list of node 0.

    {0: [1, 2, 4],
     1: [0, 2, 4],
     2: [0, 1, 3],
     3: [2, 4],
     4: [0, 1, 3],
     5: [0, 2],
     6: [2, 3, 4],
     7: [0, 1, 3]}

    Since this is the adjacency list of node 0, the address is 0. The
    ranking of a node is equal to the size of the accompanied group.
    For node 4, the size of the accompanying group '[1, 2]' is 2. The
    accompanied group in the address, size representation would be
    '{4: (0, 2)}'. The resulting accompanied groups will be the
    following:

    {1: [(2, 1), (4, 1), (7, 1)],
     2: [(1, 1), (5, 1), (0, 1)],
     3: [(2, 2), (4, 2), (7, 2), (6, 1)],
     4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

    :param adj_list: inverted adjacency list
    :type adj_list: dict
    :param L: threshold for common neighbors
    :type L: int
    :return: accompanied groups in (adress, size) representation
    :rtype: dict
    '''

    acc_group = {}

    # Find accompanied groups of nodes by address and size
    for k, v in adj_list.items():
        for i in range(1, len(v)):
            if v[i] in acc_group:
                acc_group[v[i]].append((k, i))
            else:
                acc_group[v[i]] = [(k, i)]

    return acc_group


def filter_by_lemma2(acc_group, L):
    '''Filter accompanying groups less than or equal to L

    After filtering by lemma 1, if node 'u' appears at most in L
    node adjacencies (having no greater than L accompanied groups),
    the common neighbor of any node pair containing 'u' will be no
    greater than L.

    For example, the following is a python dictionary representing
    the accompanied groups of a network.

    {1: [(2, 1), (4, 1), (7, 1)],
     2: [(1, 1), (5, 1), (0, 1)],
     3: [(2, 2), (4, 2), (7, 2), (6, 1)],
     4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

    Setting L to 3, this function will filter out nodes that have
    3 or less groups. The resulting accompanied groups will be the
    following:

    {3: [(2, 2), (4, 2), (7, 2), (6, 1)],
     4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

    :param acc_group: accompanied groups
    :type acc_group: dict
    :param L: threshold for common neighbors
    :type L: int
    :return: accompanied groups greater than L
    :rtype: dict
    '''

    f_acc_group = {}

    # Filter by L
    for k, v in acc_group.items():
        if len(v) > L:
            f_acc_group[k] = v

    return f_acc_group


def generate_node_pairs(acc_group, adj_list, L):
    '''Generate node pairs with CN greater than L.

    For example, the following is a python dictionary representing
    the accompanied groups of a network.

    {3: [(2, 2), (4, 2), (7, 2), (6, 1)],
     4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

    Rember that the accompanied groups are in (address, size) format.
    Looking at the first group for node 4, the address is pointing to
    adjacency list 1, and the size is 2. Take a look at the following
    adjacency list:

    {0: [1, 2, 4],
     1: [0, 2, 4],
     2: [0, 1, 3],
     3: [2, 4],
     4: [0, 1, 3],
     5: [0, 2],
     6: [2, 3, 4],
     7: [0, 1, 3]}

    Looking at node 1's adjacency list, the 2 other nodes accompanying
    node 4 are 0 and 2. This means that node 0, 2, and 4 share the same
    common neighbor node 1. If we look up the address and size for all
    groups and calculate the total common neighbors shared, we get the
    following:

       |_0_|_1_|_2_|_3_|
     3 | 3 | 2 | 2 |   |
     4 | 1 | 1 | 1 | 1 |

    :param acc_group: accompanied groups
    :type acc_group: dict
    :param adj_list: inverted adjacency list
    :type adj_list: dict
    :return: node pairs and CN values
    :rtype: list
    '''

    node_pairs = {}

    for k, v in acc_group.items():
        for i in v:
            # Read adjaceny list up to size (rank)
            for j in adj_list[i[0]][:i[1]]:
                node_pairs[(k, j)] = node_pairs.get((k, j), 0) + 1

    filtered_node_pairs = []

    for k, v in node_pairs.items():
        if v > L:
            filtered_node_pairs.append((k, v))

    return filtered_node_pairs


def link_prediction(c_pairs, adj_list, limit):
    '''Infer the most likely links between nodes in static network

    This function infers the mostly likely links between nodes
    based on the number of common neighbors.

    :params adj_list: adjacency list
    :type adj_list: dict
    :params c_pairs: candidate node pairs
    :type c_pairs: pandas dataframe
    :params limit: limit number of results returned
    :type limit: int
    :return: predicted links between nodes
    :rtype: list
    '''

    predictions = []

    count = 0

    for i, r in c_pairs.iterrows():
        if count <= limit:
            # keys in the adj_list dict are string type
            if str(r[1]) in adj_list.get(str(r[0]), 0):
                continue
            else:
                predictions.append((r[0], r[1]))
                count += 1

    return predictions


def save_predicted_links(predicted_links, file_name):
    '''Save predicted link as text file

    :params predicted_links: predicted node pairs
    :type predicted_links: nested list
    :params file_name: file name and save location
    :type file_name: str
    '''

    with open(file_name, "w") as f:
        for i in predicted_links:
            f.write('{} {}\n'.format(i[0], i[1]))


class TestFilter(unittest.TestCase):

    # Run before every single test
    def setUp(self):
        self.threshold = 3

        self.adj_list_1 = {0: [1, 2, 4, 5, 7],
                           1: [0, 2, 4, 7],
                           2: [0, 1, 3, 5, 6],
                           3: [2, 4, 6, 7],
                           4: [0, 1, 3, 6],
                           5: [0, 2],
                           6: [2, 3, 4],
                           7: [0, 1, 3]}

        self.adj_list_2 = {0: [1, 2, 4, 5, 7],
                           1: [0, 2, 4, 7],
                           2: [0, 1, 3, 5, 6],
                           3: [2, 4, 6, 7],
                           4: [0, 1, 3, 6]}

        self.inv_list = {0: [1, 2, 4],
                         1: [0, 2, 4],
                         2: [0, 1, 3],
                         3: [2, 4],
                         4: [0, 1, 3],
                         5: [0, 2],
                         6: [2, 3, 4],
                         7: [0, 1, 3]}

        self.acc_group_1 = {1: [(2, 1), (4, 1), (7, 1)],
                            2: [(1, 1), (5, 1), (0, 1)],
                            3: [(2, 2), (4, 2), (7, 2), (6, 1)],
                            4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

        self.acc_group_2 = {3: [(2, 2), (4, 2), (7, 2), (6, 1)],
                            4: [(1, 2), (0, 2), (3, 1), (6, 2)]}

        self.pair_node = [((4, 2), 4)]

    def test_filter_lemma1(self):
        #print("Test filter lemma 1...")
        self.assertEqual(filter_by_lemma1(self.adj_list_1, self.threshold), self.adj_list_2)

    def test_inverted_adjacency_list(self):
        #print("Test inverted_adjacency...")
        self.assertEqual(invert_adjacency_list(self.adj_list_2), self.inv_list)

    def test_generate_accompanied_groups(self):
        # print("Test both lemma filters...")
        self.assertCountEqual(generate_accompanied_groups(self.inv_list), self.acc_group_1)

    def test_filter_lemma2(self):
        self.assertEqual(filter_by_lemma2(self.acc_group_1, self.threshold), self.acc_group_2)

    def test_pair_node(self):
        self.assertEqual(generate_node_pairs(self.acc_group_2, self.inv_list, self.threshold), self.pair_node)


if __name__ == '__main__':

    unittest.main(verbosity=2)
    sys.exit()

    if '../data/adjacency_list.txt' not in os.listdir():
        print('adjacency_list.txt file was not found. Proceed to \
            create this file? (Y/N)')

        if sys.argv[0] == 'Y':

            print('Creating network graph. Reading edgelist from \
                network.tsv file (may take 5-10 min)...')

            start_time = time.time()

            with open("../data/network.tsv", 'rb') as f:
                grph = nx.read_edgelist(path=f,
                                        delimiter='\t',
                                        encoding='utf8')

            end_time = time.time()

            print("Network graph created. Process took {:.04f} \
                seconds".format(end_time - start_time))

            # Write and save adjacency list
            print('Saving network as an adjacency list...')
            adj_list_to_file(grph, './adjacency_list.txt')
            print('\'adjacency_list.txt\' was successfully \
                created!')

        if sys.argv[0] == 'N':
            print('Exiting program')
            sys.exit()

    print('Reading \'adjacency_list.txt\' file and creating a \
        dictionary...')

    adj_list = {}

    with open('./adjacency_list.txt', 'r') as f:
        # For each line in the file, create a dictionary that has a
        # key = node and value = edges
        for line in f:
            adj_list[line.split(',')[0]] = line.split(',')[1].\
            rstrip().split(' ')

    print('Dictionary created!')

    # Define Threshold
    L = 50

    print('Finding candidate nodes at threshold L = {}...'.format(L))

    # Generate candidate node pairs
    print("Step 1: Filter adjacency list")
    f_adj_list = filter_by_lemma1(adj_list, L)

    print("Step 2: Invert adjacency list")
    inv_adj_list = invert_adjacency_list(f_adj_list)

    # Clear Variables
    f_adj_list = None

    print("Step 3: Create accompanied groups")
    acc_groups = generate_accompanied_groups(inv_adj_list)

    print("Step 4: Filter accompanied groups")
    f_acc_groups = filter_by_lemma2(acc_groups, L)

    # Clear variables
    acc_groups = None

    candidate_node_pairs = generate_node_pairs(f_acc_groups,
                                               inv_adj_list,
                                               L)

    print("Candidate node pairs generated!")

    # Clear variables
    f_acc_groups = None
    inv_adj_list = None

    # Save output
    print('Saving candidate pairs as csv file...')
    save_candidate_pairs(candidate_node_pairs,
                        '../data/candidate_pairs.csv')

    print('\'candidate_pairs.csv\' was successfully created!')

    # From the candidate nodes, sort them by highest CN, then find
    # the pairs that are not already connected.
    # limit output to 50000 potential links
    limit = 500000
    print('Finding the {} most likely node pairs...'.format(limit))

    # Load candidate nodes as pandas dataframe
    candidate_nodes = pd.read_csv('../data/candidate_pairs.csv',
                              dtype={'node1': np.int32,
                                     'node2': np.int32,
                                     'CN': np.int32})

    # Sort by CN value
    candidate_nodes.sort_values('CN', inplace=True, ascending=False)

    # Predict most likey links
    predicted_links = link_prediction(candidate_nodes,
                                      adj_list,
                                      limit)

    print('Predictons complete!')

    # Save output
    print('Saving predictions as text file...')
    save_predicted_links(predicted_links,
                         '../data/predicted_links.txt')

    print('\'predicted_links.txt\' was successfully created!')

    # Check that results don't exist in adj_list already. In other
    # words, they are newly inferred links. If all links are valid
    # nothing will be printed.
    for i in predicted_links:
        if str(i[1]) in adj_list.get(str(i[0]), 0):
            print('Link between {} and {} already exists! This link \
                is not a valid prediction.'.format(i[0], i[1]))

