from Solver import Solver
from LinearProblem import LinearProblem
from sympy import Matrix, pprint
from Constrain import Constrain
from Input import Input
from CoreSimplex import CoreSimplex
from SubscriptSuperscriptLists import SubscriptSuperscriptLists


class TwoPhase(Solver):
    atrificalVariables = []
    num_unRes = None
    needphase1 = False

    def SetLinearProblem(self):
        self.LP = LinearProblem()
        self.LP.n = self.input.n
        self.LP.m = self.input.m
        self.LP.variables = self.input.symbol_map.copy()
        for key, value in self.LP.variables.items():
            self.LP.non_basic_variables.append(key)

        self.LP.basic_variables = [None] * self.LP.m
        self.LP.tableau = self.get_table()
        self.LP.maximize = self.input.maximize

        self.coresimplex = CoreSimplex(self.LP)
        # pprint(self.LP.tableau)
        # print(self.LP.variables)
        # print(self.LP.non_basic_variables)
        # print(self.LP.basic_variables)

    def solve(self):
        if (self.needphase1):
            if self.phase1():
                print("Phase one Solved with state : ", self.LP.state)
                self.LP.steps += "Phase one Solved with state : " + self.LP.state+"\n\n"
                print("\n")
                self.LP.steps += "\n"
                self.phase2()
        else:
            print("No need to Phase one\n")
            self.phase2()

        self.printSolution()
        print("Solved with Two Phase Method\n")

    def get_table(self):
        self.subscribts = SubscriptSuperscriptLists()
        num_artificiale = 0
        for constraint in self.input.constraints:
            if constraint.type == ">=":
                num_artificiale += 1
        self.num_unRes = 0
        for unrestricted in self.input.unrestricted:
            if unrestricted:
                self.num_unRes += 1
                num_artificiale += 1

        self.LP.table_cols = self.input.m + num_artificiale + self.input.n + 1
        self.LP.table_rows = self.input.m + 1

        m = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)

        i = 1
        z_artificial = [0] * self.LP.table_cols
        slack = 0

        for constraint in self.input.constraints:
            k = 0
            for j in range(self.input.n):
                if self.input.unrestricted[j]:
                    m[i, k] = constraint.coef[j]
                    self.LP.variables[k] = self.subscribts.xpluslist[j]
                    k += 1
                    m[i, k] = -1 * constraint.coef[j]
                    self.LP.variables[k] = self.subscribts.xminuslist[j]
                    if self.LP.non_basic_variables.count(k) == 0:
                        self.LP.non_basic_variables.append(k)

                else:
                    m[i, k] = constraint.coef[j]
                    self.LP.variables[k] = self.subscribts.xlist[j]
                k += 1

            if constraint.type == "<=":
                m[i, self.LP.n+slack+self.num_unRes] = 1
                self.LP.basic_variables[i - 1] = self.LP.n+slack+self.num_unRes
                self.LP.variables[self.LP.n+slack +
                                  self.num_unRes] = self.subscribts.slist[i-1]
                slack += 1

            elif constraint.type == ">=":
                m[i, self.LP.n+slack+self.num_unRes] = -1
                self.LP.variables[self.LP.n+slack +
                                  self.num_unRes] = self.subscribts.elist[i-1]
                self.LP.non_basic_variables.append(
                    self.LP.n+slack+self.num_unRes)
                slack += 1
                m[i, self.LP.n+slack+self.num_unRes] = 1
                self.LP.basic_variables[i - 1] = self.LP.n+slack+self.num_unRes
                self.LP.variables[self.LP.n+slack +
                                  self.num_unRes] = self.subscribts.alist[i-1]
                self.atrificalVariables.append(self.LP.n+slack+self.num_unRes)
                z_artificial[self.LP.n+slack+self.num_unRes] = -1
                slack += 1

            elif constraint.type == "=":
                m[i, self.LP.n+slack+self.num_unRes] = 1
                self.LP.basic_variables[i - 1] = self.LP.n+slack+self.num_unRes
                self.LP.variables[self.LP.n+slack +
                                  self.num_unRes] = self.subscribts.alist[i-1]
                self.atrificalVariables.append(self.LP.n+slack+self.num_unRes)
                z_artificial[self.LP.n+slack+self.num_unRes] = -1
                slack += 1

            m[i, self.LP.table_cols - 1] = constraint.solution
            i += 1

        for j in range(len(z_artificial)):
            m[0, j] = z_artificial[j]
        if len(self.atrificalVariables) > 0:
            self.needphase1 = True
        return m

    def phase1(self):
        print("\n" + "=" * 60)
        print(" PHASE ONE  ".center(60))
        print("=" * 60)
        print("\n")
        self.LP.steps += "PHASE ONE\n\n"
        self.LP.phaseOne = True
        print("Initial Tableau with artificial variables\n")
        self.LP.steps += "Initial Tableau with artificial variables\n\n"
        self.coresimplex.DecorateSteps(self.LP)
        for i in range(len(self.LP.basic_variables)):
            factor = self.LP.tableau[0, self.LP.basic_variables[i]]
            if factor != 0:
                self.LP.tableau[0, :] -= factor * self.LP.tableau[i + 1, :]
        print("Update Z Row ..............\n")
        self.LP.steps += "Update Z Row\n\n"
        self.LP.maximize = False
        self.coresimplex.solve()
        if (self.LP.tableau[0, self.LP.table_cols - 1] + 0 == 0 and (self.LP.state == "optimal" or self.LP.state == "Degeneracy")):
            return True
        else:
            self.LP.state = "infeasible"
            return False

    def phase2(self):
        print("\n" + "=" * 60)
        print(" PHASE TWO  ".center(60))
        self.LP.steps += "PHASE TWO\n\n"
        print("=" * 60)
        print("\n")
        self.LP.phaseOne = False
        z = [0] * self.LP.table_cols
        k = 0
        for i in range(len(self.input.zRow)):
            z[k] = -self.input.zRow[i]
            k += 1
            if (self.input.unrestricted[i]):
                z[k] = self.input.zRow[i]
                k += 1

        print("Insert Original Objective Function..........\n")
        self.LP.steps += "Insert Original Objective Function\n\n"

        for j in range(len(z)):
            self.LP.tableau[0, j] = z[j]

        self.coresimplex.DecorateSteps(self.LP)

        prevAritificalVariables = {}
        handledVar = {}
        for index, var in enumerate(self.LP.variables):
            prevAritificalVariables[index] = 0

        for a in self.atrificalVariables:
            if (a in self.LP.basic_variables):
                self.LP.tableau.row_del(self.LP.basic_variables.index(a)+1)
                self.LP.basic_variables.remove(a)
            if (a in self.LP.non_basic_variables):
                self.LP.non_basic_variables.remove(a)
            for index, var in enumerate(self.LP.variables):
                if (index > a):
                    prevAritificalVariables[index] += 1

        for i in range(len(self.atrificalVariables)-1, -1, -1):
            self.LP.tableau.col_del(self.atrificalVariables[i])
            self.LP.table_cols -= 1
        for index, var in (self.LP.variables).items():
            if (index not in self.atrificalVariables):
                handledVar[index-prevAritificalVariables[index]] = var
                if index in self.LP.basic_variables:
                    i = self.LP.basic_variables.index(index)
                    self.LP.basic_variables[i] = index - \
                        prevAritificalVariables[index]
                elif index in self.LP.non_basic_variables:
                    i = self.LP.non_basic_variables.index(index)
                    self.LP.non_basic_variables[i] = index - \
                        prevAritificalVariables[index]
        self.LP.variables = handledVar

        #  for a in self.atrificalVariables:
        #     if a in self.LP.basic_variables:
        #         indx=self.LP.basic_variables.index(a)
        #         self.LP.basic_variables.remove(a)
        #         self.LP.tableau.row_del(indx+1)
        #         self.LP.table_rows-=1

        print("Removing Atrifical Variables ..........\n")
        self.LP.steps += "Removing Atrifical Variables\n\n"
        self.coresimplex.DecorateSteps(self.LP)
        print("Update Z Row ..............\n")
        self.LP.steps += "Update Z Row\n\n"

        for i in range(len(self.LP.basic_variables)):

            factor = self.LP.tableau[0, self.LP.basic_variables[i]]

            if factor != 0:
                self.coresimplex.gaussJordan(
                    self.LP.tableau, i+1, self.LP.basic_variables[i])

        self.LP.maximize = self.input.maximize
        self.coresimplex.LP = self.LP
        self.coresimplex.solve()


# constraints = [
#     Constrain([1,1, 1], "=", 7, 1),
#     Constrain([2,-5, 1], ">=", 10, 1),
# ]

# input_data = Input( ## sheet ex done
#     n=3,
#     m=2,
#     constraints=constraints,
#     zRow=[1, 2,1],
#     maximize=True,
#     isGoal=False,
#     unrestricted=[False, False,False],
#     symbol_map={0: "x1", 1: "x2", 2: "x3"}
# )


# constraints = [
#     Constrain([3,1], "=", 3, 1),
#     Constrain([4,3], ">=", 6, 1),
#     Constrain([1,2], "<=",4, 1)
# ]

# input_data = Input(
#     n=2,
#     m=3,
#     constraints=constraints,
#     zRow=[4,1],
#     maximize=False,
#     isGoal=False,
#     unrestricted=[False, False],
#     symbol_map={0: "x1", 1: "x2"}
# )
# input_data = Input( #unrerstricted ## table view has error
#       n=2,
#       m=2,
#       constraints=[
#          Constrain([5, -1], "<=", 30, 1),
#          Constrain([1, 0], "<=", 5, 1)
#       ],
#       zRow=[30,-4],maximize=True,isGoal=False,
#       unrestricted=[False,True],
#       symbol_map={0: "x1", 1: "x2"}
#    )
# )
# input_data = Input( #unrestricted objective function
#       n=2,
#       m=2,
#       constraints=[
#          Constrain([5, -1], "<=", 30, 1),
#          Constrain([1, 0], "<=", 5, 1)
#       ],
#       zRow=[30,-4],maximize=True,isGoal=False,
#       unrestricted=[False,True],
#       symbol_map={0: "x1", 1: "x2"}
#    )

# input_data = Input( #unrestricted
#       n=2,
#       m=3,
#       constraints=[
#          Constrain([3, 2], "<=", 30, 1),
#          Constrain([2, 4], "<=", 24, 1),
#          Constrain([0, 1], ">=", 4, 1)
#       ],
#       zRow=[5,3],maximize=True,isGoal=False,
#       unrestricted=[True,False],
#       symbol_map={0: "x1", 1: "x2"}
# )
# constraints = [
#     Constrain([2,1], "<=", 2, 1),
#     Constrain([3,4], ">=", 12, 1),
# ]

# input_data = Input(  #infeasible
#     n=2,
#     m=2,
#     constraints=constraints,
#     zRow=[3, 2],
#     maximize=True,
#     isGoal=False,
#     unrestricted=[False, False],
#     symbol_map={0: "x1", 1: "x2"}
# )

# input_data = Input( #unboundeded
#       n=2,
#       m=2,
#       constraints=[
#          Constrain([7, 2], ">=", 28, 1),
#          Constrain([2, 12], ">=", 24, 1)
#       ],
#       zRow=[50,100],maximize=True,isGoal=False,
#       unrestricted=[False,False],
#       symbol_map={0: "x1", 1: "x2"}
# )
# input_data = Input( #reference !! done ☺️ 25,5,5
#       n=2,
#       m=3,
#       constraints=[
#          Constrain([0.5, 0.25], "<=", 4, 1),
#          Constrain([1, 3], ">=", 20, 1),
#          Constrain([1, 1], "=", 10, 1)
#       ],
#       zRow=[2,3],maximize=False,isGoal=False,
#       unrestricted=[False,False],
#       symbol_map={0: "x1", 1: "x2"}
# )
# input_data = Input( #reference !!infeasible true
#       n=2,
#       m=3,
#       constraints=[
#          Constrain([0.5, 0.25], "<=", 4, 1),
#          Constrain([1, 3], ">=", 36, 1),
#          Constrain([1, 1], "=", 10, 1)
#       ],
#       zRow=[2,3],maximize=False,isGoal=False,
#       unrestricted=[False,False],
#       symbol_map={0: "x1", 1: "x2"}
# )
# input_data = Input( #reference z=5 x2 = 2, x1 = 1
#       n=2,
#       m=3,
#       constraints=[
#          Constrain([1, 1], ">=", 3, 1),
#          Constrain([2, 1], "<=", 4, 1),
#          Constrain([1, 1], "=", 3, 1)
#       ],
#       zRow=[3,1],maximize=True,isGoal=False,
#       unrestricted=[False,False],
#       symbol_map={0: "x1", 1: "x2"}
#  )

# solver = TwoPhase(input_data)
# solver.SetLinearProblem()
# solver.solve()
