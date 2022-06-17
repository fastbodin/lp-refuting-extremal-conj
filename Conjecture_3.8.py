import gurobipy as gp
from gurobipy import GRB

# The following class defines an LP to solve the maximum size of an intersecting family
# of (n choose k) such that the intersection of said family with the partition is of
# the right size (given by paritions_size).
# Modify the class calls after the definition of the class to run the problem for various parameters.

class LP:
    def __init__(self, n, k, partitions, partitions_size):

        # problem is a maximization problem
        model = gp.Model('')
        model.Params.LogToConsole = 0

        # generate all possible subset of [n] of size k
        def generate_all_possible_subsets_of_n_of_size_k(binarystrings, localstring, index, cost):
            # if there is a subset of size k
            if cost == k:
                # test to see if it has the correct intersection size for each partition X_i
                for i in range(len(partitions)):
                    num_intersected = 0
                    for index in range(n):
                        if (localstring[index] + partitions[i][index]) == 2:
                            num_intersected += 1
                    # if set is not intersect with at least k_i elements
                    if num_intersected < partitions_size[i]:
                        return
                # did not fail, therefore string is intersecting correctly with each partition X_i
                binarystrings.append(tuple(localstring))
                return

            # reached the end of the string
            if index == n:
                return

            localstring[index] = 1
            # proceed with element corresponding to index + 1 is included in subset
            generate_all_possible_subsets_of_n_of_size_k(binarystrings, localstring, index + 1, cost + 1)

            localstring[index] = 0
            # proceed with element corresponding to index + 1 is not included in subset
            generate_all_possible_subsets_of_n_of_size_k(binarystrings, localstring, index + 1, cost)

        # all the subset of [n] of size k
        binarystrings = []
        generate_all_possible_subsets_of_n_of_size_k(binarystrings, [0 for i in range(n)], 0, 0)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n1 + n2 entries)] corresponds
        # with a subset of the union of the partitions with the correct pair-wise intersection size
        variables = model.addVars(binarystrings, name = 'subsets', vtype=GRB.BINARY)

        # function to determine whether the intersection of the two sets is empty
        def int_check(string1, string2):
            for index in range(n):
                # if both subsets contain the element index + 1
                if (string1[index] + string2[index]) == 2:
                    return 0
            # the intersection of the two sets is empty
            return 1

        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(binarystrings)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(binarystrings)):
                setone = binarystrings[i]
                settwo = binarystrings[j]
                # if their intersection is empty
                if int_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        print('Max size of set is {}'.format(int(model.objVal)))
        print('The elements of this max set are as follows.')
        for theset in binarystrings:
            if variables[theset].x == 1:
                print(theset)
#        antichain = ""
#        for theset in (binarystrings):
#            if variables[theset].x == 1:
#                local_set = ""
#                for index in range(n):
#                    if theset[index] == 1:
#                        local_set += str(index + 1)
#                lenthofstring = len(local_set)
#                local_set += ", "
#                antichain += local_set
#        lengthofantichain = len(antichain)
#        antichain = antichain[:lengthofantichain - 2]
#        print(antichain)


###########################
# input function calls here
###########################

#LP(7,4,[[1,1,1,0,0,0,0], [0,0,0,1,1,1,1]], [1,2])
LP(8,4,[[1,1,1,1,0,0,0,0], [0,0,0,0,1,1,1,1]], [2,1])
