import gurobipy as gp
from gurobipy import GRB
import math

# The following class defines an LP to solve the maximum size of an family F
# of 2^{[n]} without s disjont elements
# Modify the class calls after the definition of the class to run the problem for various parameters.

class LP:
    def __init__(self, n):

        # problem is a maximization problem
        model = gp.Model('LP')
        model.Params.LogToConsole = 0

        # generate all possible subset of [n]
        def generate_all_possible_subsets(binarystrings, localstring, index):
            if index == n:
                binarystrings.append(tuple(localstring))
                # reached the end of the string
                return
            # proceed with element corresponding to index + 1 is not included in subset
            localstring[index] = 0
            # proceed to next element
            generate_all_possible_subsets(binarystrings, localstring, index + 1)

            # proceed with element corresponding to index + 1 is included in subset
            localstring[index] = 1
            # proceed to next element
            generate_all_possible_subsets(binarystrings, localstring, index + 1)

        # all the subset of [n]
        binarystrings = []
        generate_all_possible_subsets(binarystrings, [0 for i in range(n)], 0)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n entries)] corresponds to the subset of [n]
        #For example variables[(0,1,1)] corresponds with the subset {2,3} of [3]
        variables = model.addVars(binarystrings, name = 'subsets', vtype=GRB.BINARY)

        # function to determine whether the four sets are pairwise disjoint
        def int_check(string1, string2, string3, string4):
            for index in range(n):
                # if both subsets contain the element index + 1
                if (string1[index] + string2[index] + string3[index] + string4[index]) > 1:
                    return 0
            # the sets are pairwise disjoint
            return 1

        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(binarystrings)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(binarystrings)):
                for k in range(j+1, len(binarystrings)):
                    for l in range(k+1, len(binarystrings)):
                        setone = binarystrings[i]
                        settwo = binarystrings[j]
                        setthree = binarystrings[k]
                        setfour = binarystrings[l]
                        # if the sets are pairwise disjoint
                        if int_check(setone, settwo, setthree, setfour):
                            # at most 3 of them can be in the family
                            model.addConstr(variables[setone] + variables[settwo] + variables[setthree] + variables[setfour] <= 3)


        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        print('begun solve')
        model.optimize()

        formula = 480
        print('Max size a family F of 2^{} without 3 pairwise disjoint members is {} >= {}'.format(n, int(model.objVal), formula))
        print('The elements of this max set are as follows.')
        for theset in binarystrings:
            if variables[theset].x == 1:
                print(theset)

###########################
# input function calls here
###########################

LP(9)
