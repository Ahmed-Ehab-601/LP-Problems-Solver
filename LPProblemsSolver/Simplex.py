from Solver import Solver
from LinearProblem import LinearProblem
from LPsolver import LPSolver
from sympy import Matrix, pprint
from Input import Input
from Constrain import Constrain
class Simplex(Solver):
    def SetLinearProblem(self):
       self.LP.n = self.input.n
       self.LP.m = self.input.m
       self.unrestricted_count = 0
       for i in self.input.unrestricted:
           if i:
               self.unrestricted_count += 1
       self.LP.table_rows = self.LP.m + 1
       self.LP.table_cols =  self.LP.n+self.LP.m+self.unrestricted_count+1
       self.LP.basic_variables = []
       self.LP.non_basic_variables= []
       self.LP.maximize = self.input.maximize
    
       self.LP.tableau = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)
       delta = 0
       for i in range(self.LP.n):
          self.LP.tableau[0,i+delta] = -self.input.zRow[i]
          if(self.input.unrestricted[i]):
             self.LP.tableau[0,i+delta+1] = self.input.zRow[i]
             self.LP.variables[i+delta] = self.input.symbol_map[i]+ "\u207A"
             self.LP.variables[i+delta+1] = self.input.symbol_map[i]+ "\u207B"
             self.LP.non_basic_variables.append(i+delta)
             self.LP.non_basic_variables.append(i+delta+1)
             delta+=1
          else:
             self.LP.variables[i+delta] = self.input.symbol_map[i]
             self.LP.non_basic_variables.append(i+delta)
             
       slack = self.LP.n+delta #index next slack   
       for i in range(self.LP.m):
          cons = self.input.constraints[i]
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
          
        

       
       
    def solve(self):
       print("Initial Tableau")
       print("")
       self.coresimplex.LP = self.LP
       self.LP = self.coresimplex.solve()
       print(self.LP.state)
       #self.printSolution()
       
    
# def test():  
#    input = Input( #optimal easy simplex
#     n=2,
#     m=4,
#     constraints=[
#         Constrain([6, 4], "<=", 24, 1),
#         Constrain([1, 2], "<=", 6, 1),
#         Constrain([-1, 1], "<=", 1, 1),
#         Constrain([0, 1], "<=", 2, 1)
#     ],
#     zRow=[5,4],maximize=True,isGoal=False,
#     unrestricted=[False,False],
#     symbol_map={0: "x1", 1: "x2"}
# )
#    input = Input( #degenerate
#     n=2,
#     m=2,
#     constraints=[
#         Constrain([1, 4], "<=", 8, 1),
#         Constrain([1, 2], "<=", 4, 1)
#     ],
#     zRow=[3,9],maximize=True,isGoal=False,
#     unrestricted=[False,False],
#     symbol_map={0: "x1", 1: "x2"}
# )
#    input = Input( #unboundeded
#     n=2,
#     m=2,
#     constraints=[
#         Constrain([1, -1], "<=", 10, 1),
#         Constrain([2, 0], "<=", 40, 1)
#     ],
#     zRow=[2,1],maximize=True,isGoal=False,
#     unrestricted=[False,False],
#     symbol_map={0: "x1", 1: "x2"}
# )
#    input = Input( #unrerstricted
#     n=2,
#     m=2,
#     constraints=[
#         Constrain([5, -1], "<=", 30, 1),
#         Constrain([1, 0], "<=", 5, 1)
#     ],
#     zRow=[30,-4],maximize=True,isGoal=False,
#     unrestricted=[False,True],
#     symbol_map={0: "x1", 1: "x2"}
# )

#    input = Input( #try min
#     n=4,
#     m=3,
#     constraints=[
#         Constrain([1, 2,2,4], "<=", 40, 1),
#         Constrain([2, -1,1,2], "<=", 8, 1),
#         Constrain([4,-2, 1,-1], "<=", 10, 1),
#     ],
#     zRow=[5,-4,6,-8],maximize=False,isGoal=False,
#     unrestricted=[False,False,False,False],
#     symbol_map={0: "x1", 1: "x2",2:"x3",3:"x4"}
# )

#    x = Simplex(input)
#    x.SetLinearProblem()
#    # pprint(x.LP.tableau)
#    # print(x.LP.variables)
#    # print(x.LP.basic_variables)
#    # print(x.LP.non_basic_variables)
#    x.solve()
   

# test()         
         
#alldone