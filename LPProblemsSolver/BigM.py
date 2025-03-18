from Solver import Solver
import LinearProblem
import CoreSimplex
import sympy as sp
from sympy import Matrix, pprint
from Constrain import Constrain
from Input import Input

class BigM(Solver):
   def __init__(self, input_data):
        self.input = input_data
        self.LP = LinearProblem.LinearProblem()

   def SetLinearProblem(self):
        self.LP.n = self.input.n
        self.LP.m = self.input.m

        self.LP.basic_variables = [None] * self.LP.m 
        self.LP.maximize = self.input.maximize
        
        self.LP.table_cols = self.LP.n + self.LP.m + 1 + self.input.unrestricted.count(True)
        self.LP.table_rows = self.LP.m + 1

        self.LP.tableau = self.preparetable()  
        self.coresimplex = CoreSimplex.CoreSimplex(self.LP)


   def preparetable(self):
      total_artificial = 0  
      total_slack = 0 
      unrestricted_count = self.input.unrestricted.count(True)  
      max_coeff = max(abs(c) for c in self.input.zRow)  
      if self.LP.maximize == True:     
        self.LP.known_variables["M"] = 100*max_coeff
      else: 
        self.LP.known_variables["M"] = -100*max_coeff
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
               self.LP.variables[slack_index]="s"+str(i+1) 
               slack_index += 1

         elif constraint.type in (">=", ">"):  
               self.LP.tableau[i + 1, slack_index] = -1 
               self.LP.non_basic_variables.append(slack_index)
               self.LP.variables[slack_index]="e"+str(i+1) 
               slack_index += 1  
               self.LP.tableau[i + 1, artificial_index] = 1
               self.LP.basic_variables[i] = artificial_index
               self.LP.tableau[0, artificial_index] = "M" 
               self.LP.variables[artificial_index]="a"+str(i+1)  
               artificial_index += 1  

         elif constraint.type == "=":  
               self.LP.tableau[i + 1, artificial_index] = 1
               self.LP.basic_variables[i] = artificial_index
               self.LP.tableau[0, artificial_index] = "M"
               self.LP.variables[artificial_index]="a"+str(i+1)  
 
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

      print("\nFinal Tableau:")
      pprint(self.LP.tableau)
      print(self.LP.basic_variables)
      print(self.LP.non_basic_variables)
      print(self.LP.variables)
      return self.LP.tableau
   
   def solve(self):   
      for i in range(len(self.LP.basic_variables)):
            row = i + 1
            col = self.LP.basic_variables[i]
            self.coresimplex.gaussJordan(table=self.LP.tableau, row=row, col=col)

      
      self.coresimplex.LP = self.LP
      self.coresimplex.solve()
      if(self.LP.state == "optimal" ):
          for i in range(len(self.LP.basic_variables)):
              if self.LP.variables[self.LP.basic_variables[i]].startswith("a"):
                  self.LP.state = "Infeasible"
                  break
      print(self.LP.state)
                  
 
constraints = [
    Constrain([2,1], "<=", 2, 1),
    Constrain([3,4], ">=", 12, 1),
]

input_data = Input( 
    n=2,
    m=2,
    constraints=constraints,
    zRow=[3, 2],
    maximize=True,   
    isGoal=False,  
    unrestricted=[False, False],
    symbol_map={0: "x1", 1: "x2"}
)

solver = BigM(input_data)
solver.SetLinearProblem()
solver.solve()

