import gurobipy as gp
from gurobipy import GRB
import math

# the following class defines an LP which determines the maximum size of
# a s-subset-regular k-uniform intersecting family F of [n].
# the inputs for this class are n,k,s

class LP:
    def __init__(self, n, k, s):

        # problem is a maximization problem
        model = gp.Model('LP')
        model.Params.LogToConsole = 0

        # function which generates all possible subset of [n] of size i
        def generate_all_possible_subsets_of_n_of_size_i(binarystrings, localstring, index, cost, i):
            # if there is a subset of size i
            if cost == i:
                binarystrings.append(tuple(localstring))
                return

            # reached the end of the string
            if index == n:
                return

            localstring[index] = 1
            # proceed with element corresponding to index + 1 is included in subset
            generate_all_possible_subsets_of_n_of_size_i(binarystrings, localstring, index + 1, cost + 1, i)

            localstring[index] = 0
            # proceed with element corresponding to index + 1 is not included in subset
            generate_all_possible_subsets_of_n_of_size_i(binarystrings, localstring, index + 1, cost, i)

        # all the subset of [n] of size k
        binarystrings = []
        generate_all_possible_subsets_of_n_of_size_i(binarystrings, [0 for i in range(n)], 0, 0, k)

        # all the subset of [n] of size s
        secondbinarystrings = []
        generate_all_possible_subsets_of_n_of_size_i(secondbinarystrings, [0 for i in range(n)], 0, 0, s)

        # BINARY VARIABLES
        # variables[(some string of 0s and 1s with a total of n entries)] corresponds to the subset of [n]
        #For example variables[(0,1,1)] corresponds with the subset {2,3} of [3]
        variables = model.addVars(binarystrings, name = 'subsets', vtype=GRB.BINARY)

        # function to determine whether the intersection of the two sets is empty
        def int_check(string1, string2):
            for index in range(n):
                # if both subsets contain the element index + 1
                if (string1[index] + string2[index]) == 2:
                    return 0
            # the intersection of the two sets is empty
            return 1

        # function to determine whether one set is contained in the other
        def subset_check(string1, string2):
            for index in range(n):
                # if string1 is not a subset of string2
                if string1[index] > string2[index]:
                    return 0
            # string1 is a subset of string2
            return 1

        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(binarystrings)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(binarystrings)):
                setone = binarystrings[i]
                settwo = binarystrings[j]
                if int_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)
        # iterate through all subsets of [n]
        for setone in secondbinarystrings:
            local_constraint = gp.LinExpr()
            # iterate through all the subsets of ([n] choose k)
            for settwo in binarystrings:
                # all subsets of size s have to be contained in the same number of elements of the
                # max set. Therefore, the sum of the variables which contain the set
                # secondbinarystrings[0] must be the same as the sum of the variables which contain
                # all sets of size s. Note that we could replace secondbinarystrings[0] with any
                # other set of size s, it does not matter
                if subset_check(secondbinarystrings[0], settwo):
                    local_constraint += variables[settwo]
                # if setone is contained in settwo
                if subset_check(setone, settwo):
                    local_constraint -= variables[settwo]
            model.addConstr(local_constraint == 0)

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        # Conjecture bound
        formula = int((math.factorial(n)/(math.factorial(k)*math.factorial((n-k))))/( 1 + (math.factorial(n-k)/(math.factorial(k)*math.factorial((n-2*k))))/(math.factorial(n-k-s-2)/(math.factorial(k-s-2)*math.factorial((n-2*k))))))

        if formula == int(model.objVal):
            print('Found example which is tight with the bound')
            print('Max {}-subset-regular {}-uniform intersecting family F of ([{}] choose {}) is {} = (n choose k)/( 1 + (n-k choose k)(n-k-s-2 choose k-s-2)) = {}'.format(s, k, n, k, int(model.objVal), formula))
            print('The elements of this set are as follows.')
            antichain = ""
            for theset in binarystrings:
                if variables[theset].x == 1:
                    print(theset)
# for LATEX
#                    local_set = "\\{"
#                    for index in range(n):
#                        if theset[index] == 1:
#                            local_set += str(index + 1)
#                            local_set += ", "
#                    lenthofstring = len(local_set)
#                    local_set = local_set[:lenthofstring - 2]
#                    local_set += "\\}, "
#                    antichain += local_set
#            lengthofantichain = len(antichain)
#            antichain = antichain[:lengthofantichain - 2]
#            print(antichain)        
        else:
            print('Could not find example which is tight with the bound')

###########################
# input function calls here
###########################

#LP(7,3,1)
#LP(9,4,1)
LP(11,5,3)
