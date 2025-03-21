from Solver import Solver
from sympy import Matrix
from Input import Input
from Constrain import Constrain

class GoalProgramming(Solver):
    def SetLinearProblem(self):
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
             noOfextraConstraints+= 1  
                  
       self.LP.table_rows = self.LP.m + self.LP.objective_count
       self.LP.table_cols =  self.LP.n+self.LP.m+self.unrestricted_count+noOfextraConstraints+1
       self.LP.basic_variables = []
       self.LP.non_basic_variables= []
       self.LP.maximize = False
       self.LP.tableau = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)
       delta = 0
       for i in range(self.LP.n):
          if(self.input.unrestricted[i]):
             self.LP.variables[i+delta] = self.input.symbol_map[i]+"\u207A"
             self.LP.variables[i+delta+1] = self.input.symbol_map[i]+"\u207B"
             self.LP.non_basic_variables.append(i+delta)
             self.LP.non_basic_variables.append(i+delta+1)
             delta+=1
          else:
             self.LP.variables[i+delta] = self.input.symbol_map[i]
             self.LP.non_basic_variables.append(i+delta)
       currentZ = 0      
       slack = self.LP.n+self.unrestricted_count #index next slack   
       for i in range(self.LP.m):
          cons = self.input.constraints[i]
          if cons.isGoal:
            delta = 0   
            for j in range(self.LP.n):
               if self.input.unrestricted[j]:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j]
                  self.LP.tableau[i+self.LP.objective_count,j+delta+1] = -cons.coef[j]
                  delta+=1 
               else:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j] 
            
            self.LP.tableau[i+self.LP.objective_count,slack] = -1
            self.LP.variables[slack] = self.subscribts.spluslist[i]
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,slack] = 1
            self.LP.variables[slack] = self.subscribts.sminuslist[i]
            key = self.subscribts.plist[i]
            self.LP.known_variables[key] = cons.priority
            self.LP.goal_map[cons.priority] = currentZ
            self.LP.goal_values.append(cons.priority)
            if cons.type == ">=":
               self.LP.non_basic_variables.append(slack-1)
               self.LP.basic_variables.append(slack)
               self.LP.tableau[currentZ,slack] = key
               self.LP.tableau[currentZ,slack] *= -1
            elif cons.type == "=":
               self.LP.non_basic_variables.append(slack-1)
               self.LP.basic_variables.append(slack)
               self.LP.tableau[currentZ,slack] = key
               self.LP.tableau[currentZ,slack] *= -1
               self.LP.tableau[currentZ,slack-1] = key
               self.LP.tableau[currentZ,slack-1] *= -1
            elif cons.type == "<=":
               self.LP.non_basic_variables.append(slack)  
               self.LP.basic_variables.append(slack-1)
               self.LP.tableau[currentZ,slack-1] = key
               self.LP.tableau[currentZ,slack-1] *= -1    
            currentZ+=1
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,self.LP.table_cols-1] = cons.solution
          elif cons.type == "<=":
            delta = 0   
            for j in range(self.LP.n):
               if self.input.unrestricted[j]:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j]
                  self.LP.tableau[i+self.LP.objective_count,j+delta+1] = -cons.coef[j]
                  delta+=1 
               else:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j] 
            self.LP.tableau[i+self.LP.objective_count,slack] = 1
            self.LP.variables[slack] = self.subscribts.slist[i]
            self.LP.basic_variables.append(slack)
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,self.LP.table_cols-1] = cons.solution
          elif cons.type == ">=":
            delta = 0   
            for j in range(self.LP.n):
               if self.input.unrestricted[j]:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j]
                  self.LP.tableau[i+self.LP.objective_count,j+delta+1] = -cons.coef[j]
                  delta+=1 
               else:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j] 
            self.LP.tableau[i+self.LP.objective_count,slack] = -1
            self.LP.variables[slack] = self.subscribts.elist[i]
            self.LP.non_basic_variables.append(slack)
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,slack] = 1
            self.LP.variables[slack] = self.subscribts.alist[i]
            self.LP.basic_variables.append(slack)
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,self.LP.table_cols-1] = cons.solution
          elif cons.type == "=":    
            delta = 0   
            for j in range(self.LP.n):
               if self.input.unrestricted[j]:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j]
                  self.LP.tableau[i+self.LP.objective_count,j+delta+1] = -cons.coef[j]
                  delta+=1 
               else:
                  self.LP.tableau[i+self.LP.objective_count,j+delta] = cons.coef[j] 
            
            self.LP.tableau[i+self.LP.objective_count,slack] = 1
            self.LP.variables[slack] = self.subscribts.alist[i]
            self.LP.basic_variables.append(slack)
            slack+=1
            self.LP.tableau[i+self.LP.objective_count,self.LP.table_cols-1] = cons.solution
    def solve(self):
       print("Initial Tableau\n")
       self.LP.steps += "Initial Tableau\n\n"
       self.coresimplex.DecorateSteps(self.LP)
       print("update Z rows\n")
       self.LP.steps += "update Z rows\n\n"
       self.updateZRows()
       self.LP.satisfied = self.LP.objective_count*[False]
       self.LP.goal_values.sort(reverse=True)
       for i in self.LP.goal_values:
          zIndex = self.LP.goal_map[i]
          self.LP.objective_index = zIndex
          self.coresimplex.LP = self.LP
          self.coresimplex.solve()
          if(self.LP.state == "optimal"):
            self.LP.satisfied[zIndex] = True
            print("Satisfied Goal",zIndex+1,"\n")
            self.LP.steps += "Satisfied Goal"+str(zIndex+1)+"\n\n"
          else:
               print("Can't Satisfy Goal",zIndex+1,"\n") 
               self.LP.steps += "Can't Satisfy Goal"+str(zIndex+1)+"\n\n"
       self.printSolution()
       print("Solved with Goal Programming Method\n")       
       
    def updateZRows(self):
       slack = self.LP.n+self.unrestricted_count
       for i in range(self.LP.m):
          cons = self.input.constraints[i]
          if cons.isGoal:
             if cons.type == "<=":
               self.coresimplex.gaussJordan(self.LP.tableau,i+self.LP.objective_count,slack)
               slack+=2
             else:
               slack+=1
               self.coresimplex.gaussJordan(self.LP.tableau,i+self.LP.objective_count,slack)
               slack+=1 
def test():
   
    inputtest = Input( 
        n=2, m=6,
        constraints=[
            Constrain([7, 3], "<=", 40, 100,True),
            Constrain([10, 5], "=", 60, 80,True),
            Constrain([5, 4], ">=", 35, 60,True),
            Constrain([100, 60], "<=", 600, 1),
            Constrain([200, 0], ">=", 1000, 50),
            Constrain([100, 400], "=", 1200, 80)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )
    input1 = Input( #lecture
        n=2, m=4,
        constraints=[
            Constrain([7, 3], ">=", 40, 100,True),
            Constrain([10, 5], ">=", 60, 80,True),
            Constrain([5, 4], ">=", 35, 60,True),
            Constrain([100, 60], "<=", 600, 1),
            
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )

    input2 = Input( #sheet
        n=2, m=4,
        constraints=[
            Constrain([200, 0], ">=", 1000, 50,True),
            Constrain([100, 400], ">=", 1200, 80,True),
            Constrain([0, 250], ">=", 800, 100,True),
            Constrain([1500, 3000], "<=", 15000, 1)
        ],
        zRow=[100, 60], maximize=True, isGoal=True,
        unrestricted=[False, False],
        symbol_map={0: "x1", 1: "x2"}
    )

    for case in [input1, input2]:
        print("\nRunning test case...")
        goal = GoalProgramming(case)
        goal.SetLinearProblem()   
        goal.solve()
        

test()
