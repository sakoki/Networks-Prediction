# Author: Koki Sasagawa
# Date: 11/14/2018
#
# The 5 functions:
# 1. filter_by_lemma1
# 2. invert_adjacency_list
# 3. generate_accompanied_groups
# 4. filter_by_lemma2
# 5. generate_node_pairs
# were created using the following paper as a reference:
#
# Cui W, Pu C, Xu Z, Cai S, Yang J, Michaelson A. Bounded link
# prediction in very large networks. Physics A: Statistical Mechanics
# and its Applications. 2016;457:202-214. doi:https://doi.org/10.101
# 6/j.physa.2016.03.041.

import pandas as pd
import numpy as np
import networkx as nx
import unittest


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
    :type adj_list: dict of {int : list of int}
    :param L: threshold for common neighbors
    :type L: int
    :returns: adjacency list containing nodes with more than L neighbors
    :rtype: dict of {int : list of int}
    '''

    adj_new = {}

    for k, v in adj_list.items():
        if len(v) > L:
            adj_new[k] = v

    return adj_new


def invert_adjacency_list(adj_list):
    '''Invert the adjacency matrix

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
    :type adj_list: dict of {int : list of int}
    :returns: inverted adjacency list
    :rtype: dict of {int : list of int}
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

    :param adj_list: adjacency list
    :type adj_list: dict of {int : list of int}
    :param L: threshold for common neighbors
    :type L: int
    :returns: accompanied groups in (adress, size) representation
    :rtype: dict of {int: list of tuple of (int, int)}
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
    :type acc_group: dict of {int: list of tuple of (int, int)}
    :param L: threshold for common neighbors
    :type L: int
    :returns: accompanied groups greater than L
    :rtype: dict of {int: list of tuple of (int, int)}
    '''

    f_acc_group = {}

    # Filter by L
    for k, v in acc_group.items():
        if len(v) > L:
            f_acc_group[k] = v

    return f_acc_group


def generate_node_pairs(acc_group, adj_list, L):
    '''Generate node pairs with common neighbors greater than L

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
    :type acc_group: dict of {int: list of tuple of (int, int)}
    :param adj_list: adjacency list
    :type adj_list: dict of {int : list of int}
    :returns: node pairs and CN values
    :rtype: list of tuple of ((int, int), int)
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


class TestFilter(unittest.TestCase):

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