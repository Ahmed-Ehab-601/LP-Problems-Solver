from Solver import Solver
from LinearProblem import LinearProblem
import CoreSimplex
import sympy as sp
from sympy import Matrix, pprint
from Constrain import Constrain
from Input import Input

class BigM(Solver):
   def SetLinearProblem(self):
        self.LP = LinearProblem()
        self.LP.n = self.input.n
        self.LP.m = self.input.m
        self.LP.isGoal = self.input.isGoal
        self.LP.basic_variables = [None] * self.LP.m 
        self.LP.maximize = self.input.maximize
        
        self.LP.table_cols = self.LP.n + self.LP.m + 1 + self.input.unrestricted.count(True)
        self.LP.table_rows = self.LP.m + 1
        self.coresimplex = CoreSimplex.CoreSimplex(self.LP)
        self.LP.tableau = self.preparetable()  
        


   def preparetable(self):
      total_artificial = 0  
      total_slack = 0 
      unrestricted_count = self.input.unrestricted.count(True)  
      max_coeff = max(abs(c) for c in self.input.zRow)  
      self.LP.known_variables["M"] = 100*max_coeff

      col_offset = 0 
      for j in range(self.LP.n):
                
         if self.input.unrestricted[j]:
            self.LP.non_basic_variables.append(j+col_offset)
            col_offset+=1           
            self.LP.non_basic_variables.append(j+col_offset)
         else:
            self.LP.non_basic_variables.append(j+col_offset) 
      for constraint in self.input.constraints:
         if constraint.type in (">=", ">"):
               total_slack += 1  
               total_artificial += 1  
         elif constraint.type in ("<=", "<"):
               total_slack += 1  
         elif constraint.type == "=":
               total_artificial += 1  
      
      self.LP.table_cols = self.LP.n + total_slack + total_artificial + 1 + unrestricted_count
      self.LP.tableau = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)
      
      slack_index = self.LP.n + unrestricted_count  
      artificial_index = self.LP.n + total_slack + unrestricted_count  
      for i, constraint in enumerate(self.input.constraints):
         col_offset = 0  
         for j in range(self.LP.n):
               if self.input.unrestricted[j]:
                  self.LP.tableau[i + 1, j + col_offset] = constraint.coef[j]
                  self.LP.variables[j + col_offset] = self.input.symbol_map[j]+"\u207A"
                  col_offset += 1 
                  self.LP.tableau[i + 1, j + col_offset] = -constraint.coef[j]  
                  self.LP.variables[j + col_offset] = self.input.symbol_map[j]+"\u207B"
               else:
                  self.LP.tableau[i + 1, j + col_offset] = constraint.coef[j]
                  self.LP.variables[j + col_offset] = self.input.symbol_map[j]
                 

         if constraint.type in ("<=", "<"):  
               self.LP.tableau[i + 1, slack_index] = 1
               self.LP.basic_variables[i] = slack_index  
               self.LP.variables[slack_index]=self.subscribts.slist[i]
               slack_index += 1

         elif constraint.type in (">=", ">"):  
               self.LP.tableau[i + 1, slack_index] = -1 
               self.LP.non_basic_variables.append(slack_index)
               self.LP.variables[slack_index]=self.subscribts.elist[i]
               slack_index += 1  
               self.LP.tableau[i + 1, artificial_index] = 1
               self.LP.basic_variables[i] = artificial_index
               self.LP.tableau[0, artificial_index] = "M" 
               if not self.LP.maximize:
                  self.LP.tableau[0, artificial_index] = -1 * self.LP.tableau[0, artificial_index]
               self.LP.variables[artificial_index]=self.subscribts.alist[i] 
               artificial_index += 1  

         elif constraint.type == "=":  
               self.LP.tableau[i + 1, artificial_index] = 1
               self.LP.basic_variables[i] = artificial_index
               self.LP.tableau[0, artificial_index] = "M"
               if not self.LP.maximize:
                  self.LP.tableau[0, artificial_index] = -1* self.LP.tableau[0, artificial_index]
               self.LP.variables[artificial_index]=self.subscribts.alist[i] 
 
               artificial_index += 1

         self.LP.tableau[i + 1, -1] = constraint.solution  

      col_offset = 0  
      for j in range(self.LP.n):
         if self.input.unrestricted[j]:
            self.LP.tableau[0, j + col_offset] = -self.input.zRow[j]
            col_offset += 1  
            self.LP.tableau[0, j + col_offset] = self.input.zRow[j]
         else:
            self.LP.tableau[0, j + col_offset] = -self.input.zRow[j]  

      print("Initial Tableau\n")
      self.LP.steps += "Initial Tableau\n\n"
      self.coresimplex.DecorateSteps(self.LP)
      return self.LP.tableau
   
   def solve(self): 
      print("Update Z Row\n")
      self.LP.steps += "Update Z Row\n\n"  
      for i in range(len(self.LP.basic_variables)):
            row = i + 1
            col = self.LP.basic_variables[i]
            self.coresimplex.gaussJordan(table=self.LP.tableau, row=row, col=col)

      
      self.coresimplex.LP = self.LP
      self.coresimplex.solve()
      if(self.LP.state == "optimal" or self.LP.state == "Degeneracy"):
          for i in range(len(self.LP.basic_variables)):
              if self.LP.variables[self.LP.basic_variables[i]].startswith("a") and self.LP.tableau[i+1, self.LP.table_cols-1] !=0:
                  self.LP.state = "Infeasible"
                  break
      self.printSolution()
      print("Solved with Big M Method\n")

      
                  
 
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
# input_data = Input( #unrerstricted x1=5 x2=-5
#       n=2,
#       m=2,
#       constraints=[
#          Constrain([5, -1], "<=", 30, 1),
#          Constrain([1, 0], "<=", 5, 1)
#       ],
#       zRow=[30,-4],maximize=True,isGoal=False,
#       unrestricted=[False,True],
#       symbol_map={0: "x1", 1: "x2"}
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
# input_data = Input( #reference !!infeasible true but m not -ve for debbuging
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
# input_data = Input( #reference deg z=5 x2 = 2, x1 = 1
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
# solver = BigM(input_data)
# solver.SetLinearProblem()
# solver.solve()

