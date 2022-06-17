import gurobipy as gp
from gurobipy import GRB
import math
import copy

# The following class defines an LP to solve the maximum size of a (l+1)-chain-free family
# of 2^[n] with diameter less than or equal to d. The inputs of this class are n, d, and l. 
# Modify the class calls after the definition of the class to run the problem for various values of n, d, and l.

class LP:
    def __init__(self, n, d, l):

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

        # function to determine whether a given pair A and B has a symmetric difference of > d
        def diam_check(string1, string2):
            sym_diff = []
            for index in range(n):
                # if only one of the sets contains the elements
                # then it is in their symmetric difference
                if string1[index] + string2[index] == 1:
                    sym_diff.append(index)
            # if the size of symmetric_difference is greater than d
            if len(sym_diff) > d:
                return 1
            # the size of symmetric_difference was less than d
            return 0

        # function to determine a chain of length l + 1 with the ref_base_set as the super set
        def l_chain_free(chain, index, localstring, ref_base_set):
            # if no more elements to add to the set
            if index == n:
                # check to see if the chain is an l chain 
                if len(chain) == l + 1:
                    # add constraint
                    constraint_to_for_chain = gp.LinExpr()
                    for chainset in chain:
                        constraint_to_for_chain += variables[tuple(chainset)]
                    model.addConstr(constraint_to_for_chain <= l)
                    return
                # need check no further
                return

            # check to see if the chain is an l chain 
            if len(chain) == l + 1:
                # add constraint
                constraint_to_for_chain = gp.LinExpr()
                for chainset in chain:
                    constraint_to_for_chain += variables[tuple(chainset)]
                model.addConstr(constraint_to_for_chain <= l)
                return

            # check to see if the element is already assumed by the super set of the chain 
            if ref_base_set[index] == 0:
                # proceed to the next hopeful for the chain
                l_chain_free(chain, index + 1, localstring, ref_base_set)
            # else the element corresponding with index + 1 is in the super set of the chain
            else:
                # there will be many recursive function calls
                # make a copy of the string so that it can be handed in its current
                # or new state to several recursions
                newlocalstring = copy.deepcopy(localstring)
                newchain = copy.deepcopy(chain)

                # did not remove element corresponding to index + 1
                l_chain_free(chain, index + 1, localstring, ref_base_set)

                # removed element corresponding to index + 1
                # all future chain members will not contain this element
                newlocalstring[index] = 0

                # first proceed as if this set is not in the chain 
                # note that this is a copy of the newlocalstring
                # this is so that in the following function call nothing has changed in the string
                l_chain_free(chain, index + 1, copy.deepcopy(newlocalstring), ref_base_set)

                # this new set is considered in the chain
                newchain.append(tuple(newlocalstring))
                # reset the index back down to zero because we now consider
                # subsets of this new set
                l_chain_free(newchain, 0, newlocalstring, newlocalstring)


        # CONSTRAINTS
        # iterate through all subsets
        for i in range(len(binarystrings)):
            # if we already check set corresponding to i against the set corresponding to j
            # where i < j we need not check set j against set i later
            for j in range(i+1, len(binarystrings)):
                setone = binarystrings[i]
                settwo = binarystrings[j]
                # if their symmetric difference is larger than d 
                if diam_check(setone, settwo):
                    # only one of them can be in the intersecting family
                    model.addConstr(variables[setone] + variables[settwo] <= 1)
            # check how many elements are in the set
            num_elements = 0
            base_chain_set = binarystrings[i]
            # the plan is to consider all the possible l+1 chains where this set is the 
            # superset of the chain, remember that the empty set is always a subset
            # hence we ask that the set as at least l elements rather than l+1
            for index in range(n):
                if base_chain_set[index] == 1:
                    num_elements += 1
            # we need only consider sets which have enough elements
            if num_elements >= l:
                l_chain_free([base_chain_set], 0, list(base_chain_set), list(base_chain_set))

        # OBJECTIVE FUNCTION
        obj = gp.LinExpr()
        for subset in binarystrings:
            obj += variables[subset]
        model.setObjective(obj, GRB.MAXIMIZE)

        # RUN
        model.optimize()

        #formula = int(math.factorial(n)/((math.factorial(n - math.floor(d/2))*math.factorial(math.floor(d/2)))))
        print('Max size subset of 2^{} with diameter <= {} which is ({}+1)-chain-free is {}'.format(n, d, l, int(model.objVal)))
        print('The elements of this max set are as follows.')
        antichain = ""
        for theset in reversed(binarystrings):
            if variables[theset].x == 1:
                print(theset)
#                local_set = "\\{"
#                for index in range(n):
#                    if theset[index] == 1:
#                        local_set += str(index + 1)
#                        local_set += ", "
#                lenthofstring = len(local_set)
#                local_set = local_set[:lenthofstring - 2]
#                local_set += "\\}, "
#                antichain += local_set
#        lengthofantichain = len(antichain)
#        antichain = antichain[:lengthofantichain - 2]
#        print(antichain)

###########################
# input function calls here
###########################
LP(6,5,2)
LP(7,5,2)
LP(8,5,2)
LP(8,7,2)
