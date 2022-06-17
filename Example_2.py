import gurobipy as gp
from gurobipy import GRB

# The following class defines an LP to construct the graph on n vertices
# and m edges such that the graph has the maximum number of triangles

class LP:
    def __init__(self, n, m):

        # problem is a maximization problem
        model = gp.Model('')
        model.Params.LogToConsole = 0

        def generate_all_possible_triangles(triangle_list, localstring, index, cost):
            # if there is a subset of size 3
            if cost == 3:
                triangle_list.append(tuple(localstring))
                return

            # reached the end of the string
            if index == n:
                return  

            localstring[index] = 1
            # proceed with element corresponding to index + 1 is included in subset
            generate_all_possible_triangles(triangle_list, localstring, index + 1, cost + 1)

            localstring[index] = 0
            # proceed with element corresponding to index + 1 is not included in subset
            generate_all_possible_triangles(triangle_list, localstring, index + 1, cost)

        def generate_all_possible_edges(edge_list, localstring, index, cost):
            # if there is a subset of size 2
            if cost  == 2:
                edge_list.append(tuple(localstring))
                return

            # reached the end of the string
            if index == n:
                return  

            localstring[index] = 1
            # proceed with element corresponding to index + 1 is included in subset
            generate_all_possible_edges(edge_list,  localstring, index + 1, cost + 1)

            localstring[index] = 0
            # proceed with element corresponding to index + 1 is not included in subset
            generate_all_possible_edges(edge_list, localstring, index + 1, cost)

        # all subsets of [n] of size 3
        triangle_list = []
        generate_all_possible_triangles(triangle_list,  [0 for i in range(n)], 0, 0)

        # all subsets of [n] of size 2
        edge_list = []
        generate_all_possible_edges(edge_list, [0 for i in range(n)], 0, 0)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n entries)] corresponds to the subset of [n] 
        #For example variables[(0,1,1,1)] corresponds with the subset {2,3,4} of [4]
        T = model.addVars(triangle_list, name = 'triangles', vtype=GRB.BINARY)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n entries)] corresponds to the subset of [n] 
        #For example variables[(0,1,1)] corresponds with the subset {2,3} of [3]
        E = model.addVars(edge_list, name = 'edges', vtype=GRB.BINARY)

        # CONSTRAINTS
        # iterate through all triangles
        for triangle in triangle_list:
            # determine edges of the triangles in pairs of two
            res = [idx for idx, val in enumerate(triangle) if val != 0] 
            edge1 = list(triangle)
            edge2 = list(triangle)
            edge3 = list(triangle)
            # delete one of the three edges from the triangle
            edge1[res[0]] = 0
            edge2[res[1]] = 0
            edge3[res[2]] = 0
            # if the triangle is present then so are the triangle edges
            model.addConstr(E[(tuple(edge1))] + E[(tuple(edge2))] + E[(tuple(edge3))]>=3*T[triangle] )
        # the number of edges is equal to m
        model.addConstr(sum(E.select('*','*')) == m)

        # OBJECTIVE FUNCTION
        model.setObjective(sum(T.select('*','*','*')), GRB.MAXIMIZE)
        
        # RUN
        model.optimize()
        # VALUE OF OBJECTIVE FUNCTION
        print('Graph G on {} vertices and {} edges with the maximum number of triangles: {} <= {}'.format(n, m, int(model.objVal), int((n-2)*m/3)))
        print('The triangles of this max set are as follows.')
        for theset in triangle_list:
            if T[theset].x == 1:
                print(theset)
# for LATEX
#        for theedge in edge_list:
#            if E[theedge].x == 1:
#                verts = []
#                for vert in range(n):
#                    if theedge[vert] == 1:
#                        verts.append(vert+1)
#                print("(N-{}) edge (N-{})".format(verts[0], verts[1]))


###########################
# Input function calls here
###########################

LP(6, 7)
LP(7, 8)
LP(8, 14)
LP(9, 18)
