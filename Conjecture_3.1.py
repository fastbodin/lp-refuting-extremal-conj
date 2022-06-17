import gurobipy as gp
from gurobipy import GRB
import math

# The following class defines an LP to solve the maximum size of an antichain
# of 2^[n] with diameter less than or equal to d. The inputs of this class are n and d. 
# Modify the class calls after the definition of the class to run the problem for various values of n and d

class LP:
    def __init__(self, n, d):

        # problem is a maximization problem
        model = gp.Model('antichains_of_fixed_diameter')
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

        def subset_check(string1, string2):
            for index in range(n):
                # if string1 is not a subset of string2
                if string1[index] > string2[index]:
                    return 0
            # string1 is a subset of string2
            return 1

        # function to determine whether a given pair A and B has a symmetric difference of > d
        def diam_check(string1, string2):
            sym_diff = []
            for index in range(n):
                # if only on of the sets contains the elements
                # then it is in their symmetric difference
                if string1[index] + string2[index] == 1:
                    sym_diff.append(index)
            # if the size of symmetric_difference is greater than d
            if len(sym_diff) > d:
                return 1
            # the size of symmetric_difference was less than d
            return 0


        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(binarystrings)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(binarystrings)):
                setone = binarystrings[i]
                settwo = binarystrings[j]
                # if string1 is a subset of string2
                if subset_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)
                # if their symmetric difference is larger than d 
                if diam_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        formula = int(math.factorial(n)/((math.factorial(n - math.floor(d/2))*math.factorial(math.floor(d/2)))))
        print('Max size of an antichain of 2^{} with diameter <= {} is {} <= {}'.format(n, d, int(model.objVal), formula))
        print('The elements of this max set are as follows.')
        antichain = ""
        for theset in reversed(binarystrings):
            if variables[theset].x == 1:
                print(theset)
# for LATEX
#                local_set = "\\"
#                for index in range(n):
#                    if theset[index] == 1:
#                        local_set += str(index + 1)
#                        local_set += ", "
#                lenthofstring = len(local_set)
#                local_set = local_set[:lenthofstring - 2]
#                local_set += "\\, "
#                antichain += local_set
#        lengthofantichain = len(antichain)
#        antichain = antichain[:lengthofantichain - 2]
#        print(antichain)

###########################
# input function calls here
###########################

LP(10,3)
LP(8,5)
LP(8,7)
