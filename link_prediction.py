# Import Libraries
import pandas as pd
import numpy as np
import networkx as nx
# import igraph
import time
import sys
import unittest

# Taken and modified from stack overflow: https://stackoverflow.com/questions/34917550/
# write-a-graph-into-a-file-in-an-adjacency-list-form-mentioning-all-neighbors-of
def adj_list_to_file(G, file_name):
    f = open(file_name, "w")
    for n in G.nodes():
        f.write(str(n) + ',')
        for neighbor in G.neighbors(n):
            f.write(str(neighbor) + ' ')
        f.write('\n')


# Specify constant L for filtering by nodes Common Neighbors
def filter_by_lemma1(adj_list, L):
    '''
    If the number of neighbors of a node is not greater than L, 
    remove the node pairs that contain that node since these
    pairs will not have more than L common neighbors. 
    
    :params adj_list: adjacency list of network
    :type adj_list: dict
    :params L: threshold for common neighbors 
    :type L: int
    :return: adjacency list with nodes that satisfy the threshold
    :rtype: dict
    '''
    
    adj_new = {}
    
    for k, v in adj_list.items():
        if len(v) > L:
            adj_new[k] = v
            
    return adj_new


def filter_by_lemma2(adj_list):
    '''
    In the remaining network after filtering by lemma 1, 
    if a node appears at most in L node adjacencies, 
    this node will not have more than L common neighbors. 
    
    :params adj_list: adjacency list of network
    :type adj_list: dict
    :return: inverted adjacency list of network 
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
    '''
    Generate all accompanied groups in address and size representation. 
    
    For example, 4 is a node at adjacency list 0 '[1, 2, 4]', and the 
    ranking of 4 in adjacency list 0 is equal to the size of the 
    accompanied group to 4, which is two.  
    
    The output for this node would look like the following: [4, (0, 2)]
    
    :params adj_list: lemma2 filtered adjacency list of network
    :type adj_list: dict
    :params L: threshold for common neighbors 
    :type L: int
    :return: accompanied groups in (adj adress, size) representation. 
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


def filter_accompanied_groups(acc_group, L):
    '''
    Filter accompanied groups by threshold L.
    
    :params acc_group: accompanied groups 
    :type acc_group: dict
    :params L: threshold for common neighbors 
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
    '''
    Accept filtered accompanied groups and generate node pairs and
    corresponding common neighbor values.
    
    :params acc_group: accompanied groups
    :type acc_group: dict
    :params adj_list: adjacency list filtered by lemma1 and lemma2 
    :type adj_list: dict
    :return: node pairs and CN values
    :rtype: dict
    '''

    node_pairs = {}
    
    for k, v in acc_group.items():
        for i in v:
            # Read adjaceny list up to size 
            for j in adj_list[i[0]][:i[1]]:
                node_pairs[(k, j)] = node_pairs.get((k, j), 0) + 1 
    
    f_node_pairs = []
    
    for k, v in node_pairs.items():
        # Filter out node pairs with CN below threshold
        if v > L: 
            filtered_node_pairs.append([k, v])
    
    return filtered_node_pairs


if name == '__main__':
    
    if '../data/adjacency_list.txt' not in os.listdir():
        print('adjacency_list.txt file was not found. Proceed to create this file? (Y/N)')
        
        if sys.argv[1] == 'Y': 
            print('Creating network graph. Read edgelist from network.tsv file (takes 5-10 min)...')    
            
            start_time = time.time() 
            
            with open("../data/network.tsv", 'rb') as f:
                grph = nx.read_edgelist(path=f, delimiter='\t', encoding='utf8')
            
            end_time = time.time()
            print("Network graph created. Process took {:.04f} seconds".format(end_time - start_time))
            
            # Write and save adjacency list 
            print('Saving network as an adjacency list...')
            adj_list_to_file(grph, './adjacency_list.txt')
            print('\'adjacency_list.txt\' file is successfully created!')
        
        if sys.argv[0] == 'N':
            print('Exiting program')
            sys.exit()
        
    print('Reading \'adjacency_list.txt\' file and creating dictionary...')
    adj_list = {}

    with open('./adjacency_list.txt', 'r') as f:
        # For each line in the file, create a dictionary that has a key = node and value = edges
        c = 0 
        for line in f:
            adj_list[line.split(',')[0]] = line.split(',')[1].rstrip().split(' ')
                        
    print('Dictionary created!')
    
    
