import gurobipy as gp
from gurobipy import GRB

# The following class defines an LP to solve the maximum size of a non-trivial intersecting family
# of (X_1, X_2 choose k, l). The inputs of this class are n_1, n,2, k, and l.
# Modify the class calls after the definition of the class to run the problem for various parameters.

class LP:
    def __init__(self, n1, n2, k, l):

        # problem is a maximization problem
        model = gp.Model('')
        model.Params.LogToConsole = 0

        def generate_all_possible_subsets_of_Xi(list_of_subsets_of_Xi, localstring, index, cost, desired_cost, max_length):
            # if there is a subset of size ni 
            if cost == desired_cost:
                list_of_subsets_of_Xi.append(tuple(localstring))
                return

            # reached the end of the string
            if index == max_length:
                return  

            localstring[index] = 1
            # proceed with element corresponding to index + 1 is included in subset
            generate_all_possible_subsets_of_Xi(list_of_subsets_of_Xi, localstring, index + 1, cost + 1, desired_cost, max_length)

            localstring[index] = 0
            # proceed with element corresponding to index + 1 is not included in subset
            generate_all_possible_subsets_of_Xi(list_of_subsets_of_Xi, localstring, index + 1, cost, desired_cost, max_length)

        # all the subset of X1 
        X1_subsets = []
        generate_all_possible_subsets_of_Xi(X1_subsets, [0 for i in range(n1)], 0, 0, k, n1)
        # all the subset of X2 
        X2_subsets = []
        generate_all_possible_subsets_of_Xi(X2_subsets, [0 for i in range(n2)], 0, 0, l, n2)

        # generate all the subsets that have the right intersection with X1 and X2
        X1_union_X2_subsets = []
        for setone in X1_subsets:
            for settwo in X2_subsets:
                X1_union_X2_subsets.append(setone + settwo)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n1 + n2 entries)] corresponds
        # a subset of X1 union X2 with correct intersection size with X1 and X2
        variables = model.addVars(X1_union_X2_subsets, name = 'subsets', vtype=GRB.BINARY)

        # function to determine whether the intersection of the two sets is empty
        def int_check(string1, string2):
            for index in range(n1 + n2):
                # if both subsets contain the element index + 1
                if (string1[index] + string2[index]) == 2:
                    return 0
            # the intersection of the two sets is empty 
            return 1

        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(X1_union_X2_subsets)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(X1_union_X2_subsets)):
                setone = X1_union_X2_subsets[i]
                settwo = X1_union_X2_subsets[j]
                # if their intersection is empty
                if int_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)

        # CONSTRAINTS
        for index in range(n1 + n2):
            local_list_of_sets = gp.LinExpr()
            for given_set in X1_union_X2_subsets:
                # if element corresponding to index is not in the set
                if given_set[index] == 0:
                    local_list_of_sets += variables[given_set]
            model.addConstr(local_list_of_sets >= 1)


        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in X1_union_X2_subsets:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        print('Max size of set is {}'.format(int(model.objVal)))
        print('The elements of this max set are as follows.')
        for theset in X1_union_X2_subsets:
            if variables[theset].x == 1:
                print(theset)


###########################
# input function calls here
###########################

LP(5,5,2,2)
