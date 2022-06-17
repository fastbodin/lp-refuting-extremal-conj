import gurobipy as gp
from gurobipy import GRB
import math

# The following class defines an LP to solve the maximum diversity of an intersecting family
# of 2^{[n]}. The input of this class is n and k. k is simply for they formula at the end.
# Modify the class calls after the definition of the class to run the problem for various values of n.

class LP:
    def __init__(self, n, k):

        # problem is a maximization problem
        # maximum diversity of an intersecting family of the power set of [n]
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
            generate_all_possible_subsets(binarystrings, localstring, index + 1)        # all the subset of [n] of size k

        binarystrings = []
        generate_all_possible_subsets(binarystrings, [0 for i in range(n)], 0)

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

        # ensure that the diversity is attained at the element 1
        # i.e. |F(1)| >= |F(i)| for each i
        # put another way |F(i)| - |F(1)| <= 0
        # for each i not equal to 1 (i.e. not the zero index)
        for i in range(1,n):
            local_constraint = gp.LinExpr()
            for subset in binarystrings:
                # if the element 1 is in the set
                if list(subset)[0] != 0:
                    local_constraint -= variables[subset]
                # if the element i is in the set
                if list(subset)[i] != 0:
                    local_constraint += variables[subset]
            # ensures that the diversity is attained at 1
            model.addConstr(local_constraint <= 0)

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        # sum over all variables which do not contain the element 1,  
        # that is the zeroth index
        for subset in binarystrings:
            if list(subset)[0] == 0:
                obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        # Conjecture bound
        formula = int((1/2)*(math.factorial(2*k-1)/(math.factorial(k-1)*math.factorial(2*k-1-(k-1)))))
        for i in range(k+1, 2*k):
            formula += int(math.factorial(2*k-1)/(math.factorial(i)*math.factorial(2*k-1-i)))

        # delta (F) is defined as the max_i |F(i)| where F(i) = {f : i in f}
        delta = 0
        for i in range(n):
            local_score = 0
            for subset in binarystrings:
                if list(subset)[i] == 1:
                    local_score += int(variables[subset].x) 
            if delta < local_score:
                delta = local_score 
        # diversity is defined as the size of the set less delta
        diversity = int(sum(variables[subsets].x for subsets in binarystrings) ) - delta

        if diversity > formula:
            print('Max diversity of an intersecting family F of 2^[{}] is {} > sum_{{i = k + 1}}^{{2k}} (2k choose i) = {}'.format(n, diversity, formula))
            print('The elements of this set are as follows.')
            for theset in binarystrings:
                if variables[theset].x == 1:
                    print(theset)
        else:
            print("Failed to find counter example.")

###########################
# input function calls here
###########################

k = 5
LP(2*k,k)

