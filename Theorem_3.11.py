import gurobipy as gp
from gurobipy import GRB
import copy

# a class to determine the subgraph G of a complete n partite graph with parts of
# arbitrary size which does not contain kK_3  (the parts need to have size at least 2).
# input different values of k to change the number of forbidden disjoint K_3'
# and change K_sizes to change the size of the parts of the complete
# n partite graph. Lastly change n to change the number of parts of the graph

class LP:
    def __init__(self, n, k, K_sizes):

        # problem is a maximization problem
        model = gp.Model('')
        model.Params.LogToConsole = 0

        # number of partitions
        num_partitions = len(K_sizes)
        # number of vertices
        num_verts = sum(partition for partition in K_sizes)

        # generate all possible subsets of size i of K_{n1,...,ni} with parts of size Kn_sizes[n1,...,ni]
        def generate_all_possible_edges_of_complete_multipartite_graph(binarystrings, localstring, K_index, index, cost, i):
            # found a subset of size i
            if cost == i:
                binarystrings.append(tuple(localstring))
                return
            # considered all partitions
            if K_index == num_partitions:
                return
            # no more vertices to consider in this partition
            if index == K_sizes[K_index]:
                return

            # proceed with element corresponding to index + 1 being part of a subset in this partition
            localstring[n*K_index + index] = 1
            # proceed to next partition and start at index 0
            generate_all_possible_edges_of_complete_multipartite_graph(binarystrings, localstring, K_index + 1, 0, cost + 1, i)

            # proceed with element corresponding to index + 1 not being part of a subset in this partition
            localstring[n*K_index + index] = 0
            generate_all_possible_edges_of_complete_multipartite_graph(binarystrings, localstring, K_index, index + 1, cost, i)

            # if you considered all the vertices in the partition
            if index == K_sizes[K_index]-1:
                # proceed with no vertex in this partition part of a subset.
                generate_all_possible_edges_of_complete_multipartite_graph(binarystrings, localstring, K_index + 1, 0, cost, i)

        # generate all possible edges of K_{n1,...,ni} with parts of size Kn_sizes[n1,...,ni]
        binarystrings = []
        generate_all_possible_edges_of_complete_multipartite_graph(binarystrings, [0 for i in range(num_verts)], 0, 0, 0, 2)
        # generate all possible triangles of K_{n1,...,ni} with parts of size Kn_sizes[n1,...,ni]
        trianglestrings = []
        generate_all_possible_edges_of_complete_multipartite_graph(trianglestrings, [0 for i in range(num_verts)], 0, 0, 0, 3)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of 2 non-zero entries)] corresponds
        # with an edges of K_{n1,...,ni} with parts of size Kn_sizes[n1,...,ni]
        variables = model.addVars(binarystrings, name = 'edges', vtype=GRB.BINARY)

        # from the list of triangles, generate all possible sets of k distinct triangles
        num_edge_in_k_distinct_triangles = k*3
        max_num_edge_for_constraint = k*3-1
        num_triangles = len(trianglestrings)

        def generate_all_possible_sets_of_k_distinct_triangles(k_distinct_triangles, edges, index, cost):
            # if the correct number of edges have been found
            if cost == num_edge_in_k_distinct_triangles:
                # add the constraint bounding the number of edges in the k distinct triangles
                model.addConstr(sum(variables[edge] for edge in edges) <= max_num_edge_for_constraint)
                return
            # if we have checked all the triangles already
            if index == num_triangles:
                return
            # new local triangle to be considered
            localtriangle = trianglestrings[index]

            # check to see whether the localtriangle corresponding to k_distinct_triangles[index] can be added to the
            # disjoint set
            for i in range(num_verts):
                # if two triangles share a vertex they are not disjoint
                if localtriangle[i] + k_distinct_triangles[i] > 1:
                    # continue on to the next triangle to test
                    generate_all_possible_sets_of_k_distinct_triangles(k_distinct_triangles, edges, index + 1, cost)
                    # once we return back to this point in the recursion we have already considered
                    # all the possible sets of k distinct triangle where this triangle (which
                    # is not distinct with the other triangles already added) is not included
                    # we can therefore return
                    return
            # if the recursion has not returned, this triangle is distinct with the other triangles in k_distinct_triangles
            # we proceed with this triangle included.
            generate_all_possible_sets_of_k_distinct_triangles(copy.deepcopy(k_distinct_triangles), copy.deepcopy(edges), copy.deepcopy(index) + 1, copy.deepcopy(cost))

            # now proceed with this triangle included
            k_distinct_triangles = tuple(sum(t) for t in zip(k_distinct_triangles, localtriangle))
            # determine edges of the triangles in pairs of two
            res = [idx for idx, val in enumerate(localtriangle) if val != 0]
            edge1 = list(localtriangle)
            edge2 = list(localtriangle)
            edge3 = list(localtriangle)
            # delete one of the three edges from the triangle
            edge1[res[0]] = 0
            edge2[res[1]] = 0
            edge3[res[2]] = 0
            edges.append(tuple(edge1))
            edges.append(tuple(edge2))
            edges.append(tuple(edge3))
            # if the triangle is present then so are the triangle edges
            cost += 3
            generate_all_possible_sets_of_k_distinct_triangles(k_distinct_triangles, edges, index + 1, cost)

        # create all possible k disjoint triangles
        constraint = gp.LinExpr()
        generate_all_possible_sets_of_k_distinct_triangles([0 for i in range(num_verts)], [], 0, 0)

        # OBJECTIVE FUNCTION
        print("done")
        obj = gp.LinExpr()
        for edge in binarystrings:
            obj += variables[edge]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        formula = 4*n**2 + (k-1)*n

        print('Max number of edges of K_{} which does not contain {}K_3 is {} = {}'.format(K_sizes, k, int(model.objVal), int(formula)))
        print('The elements of this max set are as follows.')
        #final = set([])
        for theset in binarystrings:
            if variables[theset].x == 1:
                print(theset)
#                final.add(theset)
#        print(final)

# for LATEX
#        for theedge in binarystrings:
#            if variables[theedge].x == 1:
#                verts = []
#                for vert in range(num_verts):
#                    if theedge[vert] == 1:
#                        verts.append(vert+1)
#                print("(N-{}) edge (N-{})".format(verts[0], verts[1]))

###########################
# input function calls here
###########################

# note that you need to have sets of size at least 2
# n, k, K_sizes
LP(4, 2, [4,4,4,4])
#LP(3, 2, [3,3,3,3])
