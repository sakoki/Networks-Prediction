# Networks-Prediction
Python script for link-prediction and attribute-prediction project. 

## Methods:

For link prediction and attribute prediction, the following 3 libraries were used:
- Pandas
- Numpy
- Networkx

For the link prediction algorithms, the paper “Bounded link prediction in very large networks” by Cui et al. (2016) was used as a reference for developing and implementing the fast algorithm for calculating common neighbors (CN) on very large networks. Some functions were written with the assistance of stack overflow, which is referenced directly in the code comments. 

## My Approach:

For link prediction, I implemented a bounded link prediction method described by Cui et al. (2016) for predicting links between nodes using common neighbors. As demonstrated in the paper, this approach was specifically designed to work with large social networks such as Facebook and Google web data.<sup>1</sup> Normally, CN based evaluations are computationally expensive and do not scale well with a time complexity of O(|v|\*k2) where V is the node set and k is the average node degree.<sup>1</sup> The data for this project was from a social network data, thus it was reasonable to infer that this methodology would be appropriate for my purposes. To efficiently manipulate and work with the graph data, a function was written to generate an adjacency list from the undirected networkx graph, which is a dictionary containing nodes as the key, and a list of all connected neighboring nodes as the value. 

The scalability of the bounded link prediction methods is largely due to the two filtering steps that reduce the number of nodes considerably. The first filter removes nodes with neighbors less than or equal to a given threshold L.<sup>1</sup>  The idea behind this rule is that any pairs containing this node will have no more than L neighbors, thus allowing it to be removed.<sup>1</sup> In the second filtering step, if a particular node ‘u’ appears at most in L node’s adjacencies, then the common neighbor of any node pair containing ‘u’ will be no greater than L.<sup>1</sup> Filtering allows us to drastically reduce the total number of nodes, making the computation much more manageable.

For the prediction task, I selected L=50 to be my threshold as that is where the curve begins to flatten and the number of nodes begin to stable out (included in the notebook). Using this threshold, I was able to narrow down on the nodes that have large CN values. These nodes are thought to make up the dense areas of the network, whereas the nodes with small CN make up the sparse areas.<sup>1</sup> As Cui et al mentions, most real-world networks have topologically heterogeneous structures, and link predictions happen in relatively dense areas of the network.<sup>1</sup> The algorithm follows the simple idea where in a social network if a user is connected to more friends (high degree), it is more likely that they share many mutual friends with the friends of their friends (high density). Hense, this leads to a greater-than-chance likelihood of meeting them and establishing a link in the future. In sparser areas of the network, users are connected to few friends (low degree) and share fewer mutual friends with their neighbors (low density), and thus, have a smaller chance of establishing a link. The bounded linked prediction model was able to predict 50000 links in a reasonable amount of time. 

For the second task of attribute prediction, three functions were created to calculate the similarity metric of neighbors of a target node. One function calculates the Jaccard similarity (neighbors with more overlapping CN are more similar), Adamic/Adar (neighbors sharing rare CN are more similar), and preferential attachment (highly connected neighbors are more likely to form links).<sup>2</sup> Using the theory of homophily, we know that nodes that share common properties are more likely to form links. With that idea, we can predict the attributes of nodes based on their connectivity to neighboring nodes. A possible limitation of my approach is that it relies only on the structure of the network to predict the likelihood of certain attributes. For nodes that are relatively sparse, it may be difficult to predict attributes based on structure alone. Both Jaccard and Adamic/Adar fail to generate similarity scores (sim score of 0) when nodes do not share any common neighbors. For these cases, I used preferential attachment to find the most likely node to inherit attributes from. Preferential attachment calculations use the degree of two nodes instead of the number of common neighbors, thus produce some numerical value to rank nodes even when there are no shared common neighbors. In fact, we see that combining preferential attachment with CN similarity measures improved the score of attribute predictions. The performance of the different approaches is summarized in the following table.

| Similarity Metric | Performance (mean F1 score) | 
|:-----------------:|:---------------------------:|
| Jaccard           | 0.75674                     |
| Adamic/Adar       | 0.75892                     |
| Jaccard + Preferential Attachment | 0.78257     |
| Adamic/Adar + Preferential Attachment | 0.814   | 

## Sources

1. Cui W, Pu C, Xu Z, Cai S, Yang J, Michaelson A. Bounded link prediction in very large networks. Physics A: Statistical Mechanics and its Applications. 2016;457:202-214. doi:https://doi.org/10.1016/j.physa.2016.03.041.
2. Liben-Nowell David and Kleinberg Jon. 2006. The link-prediction problem for social networks. Journal of the American Society for Information Science and Technology 58(7):1019–1031.
