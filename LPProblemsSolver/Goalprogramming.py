from Solver import Solver
from sympy import Matrix, pprint
from Input import Input
from Constrain import Constrain
from LinearProblem import LinearProblem


class GoalProgramming(Solver):
    atrificalVariables = []

    def SetLinearProblem(self):
        self.LP = LinearProblem()
        self.atrificalVariables = []
        if not self.input.isGoal:
            return
        self.LP.isGoal = True
        self.LP.n = self.input.n
        self.LP.m = self.input.m
        self.unrestricted_count = 0
        for i in self.input.unrestricted:
            if i:
                self.unrestricted_count += 1
        self.LP.objective_count = 0
        noOfextraConstraints = 0
        for constraint in self.input.constraints:
            if constraint.isGoal:
                noOfextraConstraints += 1
                self.LP.objective_count += 1
            elif constraint.type == ">=":
                noOfextraConstraints += 1
                self.LP.needPhaseOne = True
                self.LP.phaseOne = True
            elif constraint.type == "=":
                self.LP.needPhaseOne = True
                self.LP.phaseOne = True
        if self.LP.needPhaseOne:
            self.LP.objective_count += 1
        self.LP.table_rows = self.LP.m + self.LP.objective_count
        self.LP.table_cols = self.LP.n+self.LP.m + \
            self.unrestricted_count+noOfextraConstraints+1
        self.LP.basic_variables = []
        self.LP.non_basic_variables = []
        self.LP.maximize = False
        self.LP.tableau = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)
        delta = 0
        for i in range(self.LP.n):
            if (self.input.unrestricted[i]):
                self.LP.variables[i+delta] = self.input.symbol_map[i]+"\u207A"
                self.LP.variables[i+delta +
                                  1] = self.input.symbol_map[i]+"\u207B"
                self.LP.non_basic_variables.append(i+delta)
                self.LP.non_basic_variables.append(i+delta+1)
                delta += 1
            else:
                self.LP.variables[i+delta] = self.input.symbol_map[i]
                self.LP.non_basic_variables.append(i+delta)
        currentZ = 0
        if self.LP.needPhaseOne:
            currentZ += 1
        slack = self.LP.n+self.unrestricted_count  # index next slack
        for i in range(self.LP.m):
            cons = self.input.constraints[i]
            if cons.isGoal:
                delta = 0
                for j in range(self.LP.n):
                    if self.input.unrestricted[j]:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta+1] = -cons.coef[j]
                        delta += 1
                    else:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]

                self.LP.tableau[i+self.LP.objective_count, slack] = -1
                self.LP.variables[slack] = self.subscribts.spluslist[i]
                slack += 1
                self.LP.tableau[i+self.LP.objective_count, slack] = 1
                self.LP.variables[slack] = self.subscribts.sminuslist[i]
                key = self.subscribts.plist[i]
                self.LP.known_variables[key] = cons.priority
                if self.LP.needPhaseOne:
                  currentZ-=1
                self.LP.goal_map[cons.priority] = currentZ
                self.LP.goal_values.append(cons.priority)
                if self.LP.needPhaseOne:
                  currentZ+=1
                if cons.type == ">=":
                    self.LP.non_basic_variables.append(slack-1)
                    self.LP.basic_variables.append(slack)
                    self.LP.tableau[currentZ, slack] = key
                    self.LP.tableau[currentZ, slack] *= -1
                elif cons.type == "=":
                    self.LP.non_basic_variables.append(slack-1)
                    self.LP.basic_variables.append(slack)
                    self.LP.tableau[currentZ, slack] = key
                    self.LP.tableau[currentZ, slack] *= -1
                    self.LP.tableau[currentZ, slack-1] = key
                    self.LP.tableau[currentZ, slack-1] *= -1
                elif cons.type == "<=":
                    self.LP.non_basic_variables.append(slack-1)
                    self.LP.basic_variables.append(slack)
                    self.LP.tableau[currentZ, slack-1] = key
                    self.LP.tableau[currentZ, slack-1] *= -1
                currentZ += 1
                slack += 1
                self.LP.tableau[i+self.LP.objective_count,
                                self.LP.table_cols-1] = cons.solution
            elif cons.type == "<=":
                delta = 0
                for j in range(self.LP.n):
                    if self.input.unrestricted[j]:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta+1] = -cons.coef[j]
                        delta += 1
                    else:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                self.LP.tableau[i+self.LP.objective_count, slack] = 1
                self.LP.variables[slack] = self.subscribts.slist[i]
                self.LP.basic_variables.append(slack)
                slack += 1
                self.LP.tableau[i+self.LP.objective_count,
                                self.LP.table_cols-1] = cons.solution
            elif cons.type == ">=":
                delta = 0
                for j in range(self.LP.n):
                    if self.input.unrestricted[j]:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta+1] = -cons.coef[j]
                        delta += 1
                    else:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                self.LP.tableau[i+self.LP.objective_count, slack] = -1
                self.LP.variables[slack] = self.subscribts.elist[i]
                self.LP.non_basic_variables.append(slack)
                slack += 1
                self.LP.tableau[i+self.LP.objective_count, slack] = 1
                self.LP.variables[slack] = self.subscribts.alist[i]
                self.LP.basic_variables.append(slack)
                self.LP.tableau[0, slack] = -1
                self.atrificalVariables.append(slack)
                slack += 1
                self.LP.tableau[i+self.LP.objective_count,
                                self.LP.table_cols-1] = cons.solution
            elif cons.type == "=":
                delta = 0
                for j in range(self.LP.n):
                    if self.input.unrestricted[j]:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta+1] = -cons.coef[j]
                        delta += 1
                    else:
                        self.LP.tableau[i+self.LP.objective_count,
                                        j+delta] = cons.coef[j]

                self.LP.tableau[i+self.LP.objective_count, slack] = 1
                self.LP.variables[slack] = self.subscribts.alist[i]
                self.LP.basic_variables.append(slack)
                self.LP.tableau[0, slack] = -1
                self.atrificalVariables.append(slack)
                slack += 1
                self.LP.tableau[i+self.LP.objective_count,
                                self.LP.table_cols-1] = cons.solution
    def solve(self):
        print("Initial Tableau\n")
        self.LP.steps += "Initial Tableau\n\n"
        self.coresimplex.DecorateSteps(self.LP)
        print("update Z rows\n")
        self.LP.steps += "update Z rows\n\n"
        self.updateZRows()
        self.PhaseOne()
        if self.LP.state == "Infeasible":
           self.printSolution()
           return
        
        self.LP.satisfied = self.LP.objective_count*[False]
        self.LP.goal_values.sort(reverse=True)
        for i in self.LP.goal_values:
            zIndex = self.LP.goal_map[i]
            self.LP.objective_index = zIndex
            self.coresimplex.LP = self.LP
            print("Solve for Goal ", zIndex+1, "\n")
            self.LP.steps += "Solve for Goal "+str(zIndex+1)+"\n\n"
            self.coresimplex.solve()
            print(self.LP.state)
            if ((self.LP.state == "optimal" or self.LP.state == "Degeneracy" )and self.LP.tableau[zIndex, self.LP.table_cols-1] == 0):
                  self.LP.satisfied[zIndex] = True
                  print("Satisfied Goal", zIndex+1, "\n")
                  self.LP.steps += "Satisfied Goal"+str(zIndex+1)+"\n\n"
            else:
                  print("Can't Satisfy Goal", zIndex+1, "\n")
                  self.LP.steps += "Can't Satisfy Goal"+str(zIndex+1)+"\n\n"


        self.printSolution()

    def updateZRows(self):
        slack = self.LP.n+self.unrestricted_count
        for i in range(self.LP.m):
            cons = self.input.constraints[i]
            if cons.isGoal:
                if cons.type == "<=":
                    slack += 2
                else:
                    slack += 1
                    self.LP.tableau = self.coresimplex.gaussJordan(self.LP.tableau, i+self.LP.objective_count, slack)
                    slack += 1
            elif cons.type == "<=":
                slack += 1
            elif cons.type == ">=":
                slack += 1
                self.LP.tableau = self.coresimplex.gaussJordan(self.LP.tableau, i+self.LP.objective_count, slack)
                slack += 1
            elif cons.type == "=":
                self.LP.tableau = self.coresimplex.gaussJordan(self.LP.tableau, i+self.LP.objective_count, slack)
                slack += 1
    def PhaseOne(self):
       if not self.LP.needPhaseOne:
           return
       self.LP.isGoal = False
       self.LP.objective_index = 0
       self.coresimplex.LP = self.LP
       print("Solve for Constraints in Phase One","\n")
       self.LP.steps += "Solve for Constraints in Phase One"+"\n\n"
       self.coresimplex.solve()
       if ((self.LP.state == "optimal" or self.LP.state == "Degeneracy" )and self.LP.tableau[0, self.LP.table_cols-1] == 0):
            for i in range(len(self.LP.basic_variables)):
                  if self.LP.variables[self.LP.basic_variables[i]].startswith("a") and self.LP.tableau[i+self.LP.objective_count, self.LP.table_cols-1] != 0:
                        self.LP.state = "Infeasible"
                        break
            if(self.LP.state == "Infeasible"):
                print("Can't Satisfy >= or = Constrain Infeasible", "\n")
                self.LP.steps += "Can't Satisfy >= or = Constrain Infeasible"+"\n\n"
                self.LP.isGoal = True
                return
            print("Satisfied Constrain of >= and =", "\n")
            self.LP.steps += "Satisfied Constrain of >= and ="+"\n\n"
            self.PhaseOneDone()
            self.LP.isGoal = True            
         
       else:
            self.LP.state = "Infeasible"
            print("Can't Satisfy >= or = Constrain Infeasible", "\n")
            self.LP.steps += "Can't Satisfy >= or = Constrain Infeasible"+"\n\n"
       
       self.LP.isGoal = True
       
      
    def PhaseOneDone(self):
        self.LP.tableau.row_del(0)
        self.LP.objective_count-=1
        self.LP.table_rows-=1
        self.LP.phaseOne = False
        prevAritificalVariables ={}
        handledVar={}
        for index , var in enumerate(self.LP.variables):
           prevAritificalVariables[index]=0

        for a in self.atrificalVariables:
            if(a in self.LP.basic_variables):
               self.LP.tableau.row_del(self.LP.basic_variables.index(a)+self.LP.objective_count)
               self.LP.basic_variables.remove(a)
            if(a in self.LP.non_basic_variables):
               self.LP.non_basic_variables.remove(a)
            for index , var in enumerate(self.LP.variables):
               if (index>a):
                       prevAritificalVariables[index]+=1

        for i in range(len(self.atrificalVariables)-1,-1,-1):
            self.LP.tableau.col_del(self.atrificalVariables[i])
            self.LP.table_cols-=1
        for index , var in (self.LP.variables).items():
              if (index not in self.atrificalVariables):
                  handledVar[index-prevAritificalVariables[index]]=var
                  if index in self.LP.basic_variables:
                       i= self.LP.basic_variables.index(index)
                       self.LP.basic_variables[i]=index-prevAritificalVariables[index]
                  elif index in self.LP.non_basic_variables:
                       i= self.LP.non_basic_variables.index(index)
                       self.LP.non_basic_variables[i]=index-prevAritificalVariables[index]
        self.LP.variables = handledVar


def test():

    inputtest1 = Input(  # sat g1 and constrains x1=84/17 x2=30/17
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=5, isGoal=True),
            Constrain([10, 5], "=", 60, priority=4, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=3, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], "<=", 1000, 50),
            Constrain([100, 400], "=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest2 = Input(  # can't satisfy constrains
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=6, isGoal=True),
            Constrain([10, 5], "=", 60, priority=5, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=4, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], ">=", 1000, 50),
            Constrain([100, 400], "=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest3 = Input(  # sat g1 and g3 and constrains  x1=3 x2= 5
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=6, isGoal=True),
            Constrain([10, 5], "=", 60, priority=5, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=4, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], "<=", 1000, 50),
            Constrain([100, 400], ">=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest4 = Input(  # sat g1 and constrains  x1=5 x2= 5/3
        n=2, m=6,
        constraints=[
            Constrain([7.0, 3.0], "<=", 40.0, priority=6, isGoal=True),
            Constrain([10.0, 5.0], "=", 60.0, priority=5, isGoal=True),
            Constrain([5.0, 4.0], ">=", 35.0, priority=4, isGoal=True),
            Constrain([100.0, 60.0], "<=", 600.0, 1),
            Constrain([200.0, 0.0], "=", 1000.0, 50.0),
            Constrain([100.0, 400.0], "<=", 1200.0, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest5 = Input( # x=5, x2= 5/3 goal 1 sat
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=6, isGoal=True),
            Constrain([10, 5], "=", 60, priority=5, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=4, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], "<=", 1000, 50),
            Constrain([100, 400], "<=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest6 = Input( # x=5, x2= 5/3 goal 1 sat
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=2, isGoal=True),
            Constrain([10, 5], "=", 60, priority=5, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=3, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], "<=", 1000, 50),
            Constrain([100, 400], "<=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest7 = Input(  # same input 3 try to make col early
        n=2, m=6,
        constraints=[
            Constrain([100, 400], ">=", 1200, 80),
            Constrain([7, 3], "<=", 40, priority=6, isGoal=True),
            Constrain([5, 4], ">=", 35, priority=4, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([10, 5], "=", 60, priority=5, isGoal=True),
            Constrain([200, 0], "<=", 1000, 50),
            
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest8 = Input(  # same input1 try to change
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, priority=5, isGoal=True),
            Constrain([100, 400], "=", 1200, 80),
            Constrain([10, 5], "=", 60, priority=4, isGoal=True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], "<=", 1000, 50),
             Constrain([5, 4], ">=", 35, priority=3, isGoal=True),
           
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    inputtest9 = Input(  # sat g1 and constrains  x1=5 x2= 5/3
        n=2, m=6,
        constraints=[
            Constrain([7.0, 3.0], "<=", 40.0, priority=6, isGoal=True),
            Constrain([10.0, 5.0], "=", 60.0, priority=5, isGoal=True),
            Constrain([5.0, 4.0], ">=", 35.0, priority=4, isGoal=True),
            Constrain([100.0, 60.0], "<=", 600.0, 1),
            Constrain([200.0, 0.0], "<=", 1000.0, 50.0),
            Constrain([100.0, 400.0], ">=", 1200.0, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    input1 = Input(  # lecture
        n=2, m=4,
        constraints=[
            Constrain([7, 3], ">=", 40, 100, True),
            Constrain([10, 5], ">=", 60, 80, True),
            Constrain([5, 4], ">=", 35, 60, True),
            Constrain([100, 60], "<=", 600, 1),

        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
  

    input2 = Input(  # sheet
        n=2, m=4,
        constraints=[
            Constrain([200, 0], ">=", 1000, 2, True),
            Constrain([100, 400], ">=", 1200, 3, True),
            Constrain([0, 250], ">=", 800, 1, True),
            Constrain([1500, 3000], "<=", 15000, 1)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )

   #  for case in [input1, input2]:
   #      print("\nRunning test case...")
   #      goal = GoalProgramming(case)
   #      goal.SetLinearProblem()
   #      goal.solve()
    # goal = GoalProgramming(inputtest2)
    # goal.SetLinearProblem()
    # goal.solve()



test()
