import math
import gurobipy as gp
from gurobipy import GRB

# The following class defines an LP to solve the maximum size of an antichain
# of 2^[n]. The input of this class is n. Modify the class calls after
# the definition of the class to run the problem for various values of n

class LP:
    def __init__(self, n):

        # problem is a maximization problem
        model = gp.Model('LP')
        # suppress reporting of solver
        model.Params.LogToConsole = 0

        # generate all possible subset of [n]
        def generate_all_possible_subsets(binarystrings, localstring, index):
            # binarystrings holds the list of subsets of [n]
            # localstring is the current subsets
            # index corresponds with element index + 1 of the localstring

            # if we considered all elements
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
        for setone in binarystrings:
            # iterate through all subsets
            for settwo in binarystrings:
                # if its not the same subset
                if setone != settwo:
                    # if setone is a subset of settwo
                    if subset_check(setone, settwo):
                        # only one of them can be in the antichain
                        model.addConstr(variables[setone] + variables[settwo] <= 1)

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        # Printing some output
        formula = int(math.factorial(n)/(math.factorial(n - math.floor(n/2))*math.factorial(math.floor(n/2))))
        print('Max size of an antichain F of the power set of [{}] is {} = (n choose floor(n/2)) = {}'.format(n, int(model.objVal), formula))
        print('The elements of this max set are as follows.')
        antichain = ""
        for theset in reversed(binarystrings):
            if variables[theset].x == 1:
                local_set = ""
                for index in range(n):
                    if theset[index] == 1:
                        local_set += str(index + 1)
                lenthofstring = len(local_set)
                local_set += ", "
                antichain += local_set
        lengthofantichain = len(antichain)
        antichain = antichain[:lengthofantichain - 2]
        print(antichain)



###########################
# input function calls here
###########################

LP(3)
LP(4)
LP(5)
