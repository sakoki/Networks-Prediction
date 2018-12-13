# Networks-Prediction
Python script for link-prediction and attribute-prediction assignment. 

## Methods:

For link prediction and attribute prediction, the following 3 libraries were used:
- Pandas
- Numpy
- Networkx

Other libraries such as time, os, and pprint were used for developmental purposes. Additionally, for the link prediction algorithms, the paper “Bounded link prediction in very large networks” by Cui et al. was used as a reference for developing and implementing the fast algorithm for calculating connected neighbors on very large networks. Additionally, few functions were written with the assistance of stack overflow forms, which is linked directly in the code comments. 

## My Approach:

For link prediction, I implemented a bounded link prediction method described by Cui et al. for predicting links between nodes using common neighbors. As demonstrated in the paper, this approach was specifically designed to work on large social networks such as Facebook and Google web data.<sup>1</sup> Normally, CN based evaluations are computationally expensive and do not scale well with a time complexity of O(|v|*k2) where V is the node set and k is the average node degree.<sup>1</sup> As the network data provided for the assignment was a social network data, it was reasonable to infer that this methodology would be appropriate for my purposes. To efficiently manipulate and work with the graph data, a function was written to generate an adjacency list from the undirected networkx graph, which is a dictionary containing nodes as the key, and a list of all connected neighboring nodes as the value. 

The scalability of the bounded link prediction methods is largely due to the two filtering steps that reduce the number of nodes considerably. The first filter removes nodes with neighbors less than or equal to a given threshold L.<sup>1</sup>  The idea behind this rule is that any pairs containing this node will have no more than L neighbors, thus allowing it to be removed.<sup>1</sup> In the second filtering step, if a particular node ‘u’ appears at most in L node’s adjacencies, then the common neighbor of any node pair containing ‘u’ will be no greater than L.<sup>1</sup> Filtering allows us to drastically reduce the total number of nodes, making the computation much more manageable. The reduction in the number of nodes after the first filtering step is illustrated in the line plot in figure 1.

## Sources

1. Cui W, Pu C, Xu Z, Cai S, Yang J, Michaelson A. Bounded link prediction in very large networks. Physics A: Statistical Mechanics and its Applications. 2016;457:202-214. doi:https://doi.org/10.1016/j.physa.2016.03.041.
