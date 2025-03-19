from Solver import Solver
from LinearProblem import LinearProblem
from sympy import Matrix, pprint
from Constrain import Constrain
from Input import Input
from CoreSimplex import CoreSimplex
from SubscriptSuperscriptLists import SubscriptSuperscriptLists

class TwoPhase(Solver):
    
    atrificalVariables=[]
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
        self.coresimplex=CoreSimplex(self.LP)
        pprint(self.LP.tableau)
        print(self.LP.variables)
        print(self.LP.non_basic_variables)
        print(self.LP.basic_variables)

    def solve(self):
        if self.phase1():
            if self.phase2():
                return
        self.printSolution()
        with open("TwoPhase.txt", "w") as file:
            file.write(self.LP.steps)
      
    def get_table(self):
        self.subscribts=SubscriptSuperscriptLists()
        num_artificiale = 0
        for constraint in self.input.constraints:
            if constraint.type == ">=":
                num_artificiale += 1
        num_unRes=0
        for unrestricted in self.input.unrestricted:
            if unrestricted:
                num_unRes+=1
                num_artificiale += 1

        self.LP.table_cols = self.input.m + num_artificiale + self.input.n + 1
        self.LP.table_rows = self.input.m + 1

        m = Matrix.zeros(self.LP.table_rows, self.LP.table_cols)

        i = 1  
        z_artificial = [0] * self.LP.table_cols
        slack=0
        for constraint in self.input.constraints:
            for j in range(self.input.n):
                m[i, j] = constraint.coef[j]
                if self.input.unrestricted[j]:
                    self.LP.variables[j] = self.subscribts.xpluslist[j]
                    m[i, self.LP.n+j] = -1 * constraint.coef[j]
                    self.LP.variables[self.LP.n+j] = self.subscribts.xminuslist[j]
                    if self.LP.non_basic_variables.count(self.LP.n+j) == 0:
                        self.LP.non_basic_variables.append(self.LP.n+j)
                    
                  
                   
                
            if constraint.type == "<=":
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1]=self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = self.subscribts.slist[i-1]
                slack+=1

            elif constraint.type == ">=":
                m[i,self.LP.n+slack+num_unRes] = -1
                self.LP.variables[self.LP.n+slack+num_unRes] = self.subscribts.elist[i-1]
                self.LP.non_basic_variables.append(self.LP.n+slack+num_unRes)
                slack+=1
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1] =self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = self.subscribts.alist[i-1]
                self.atrificalVariables.append(self.LP.n+slack+num_unRes)
                z_artificial[self.LP.n+slack+num_unRes] = -1
                slack+=1
           

            elif constraint.type == "=":
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1] = self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = self.subscribts.alist[i-1]
                self.atrificalVariables.append(self.LP.n+slack+num_unRes)
                z_artificial[self.LP.n+slack+num_unRes] = -1
                slack += 1

            m[i, self.LP.table_cols - 1] = constraint.solution
            i += 1
     

        for j in range(len(z_artificial)):
            m[0, j] = z_artificial[j]
        return m

    def phase1(self):
        print("\n" + "=" * 60)
        print(" PHASE ONE  ".center(60))
        print("=" * 60)
        print("\n")
        self.LP.steps += "PHASE ONE\n\n"
        self.LP.phase1 = True
        print("Initial Tableau with artificial variables\n" )
        self.LP.steps += "Initial Tableau with artificial variables\n\n"
        self.coresimplex.DecorateSteps(self.LP)
        for i in range(self.LP.m):
            factor = self.LP.tableau[0, self.LP.basic_variables[i]]
            if factor != 0:
                self.LP.tableau[0, :] -= factor * self.LP.tableau[i + 1, :]
        print("Update Z Row ..............\n")
        self.LP.steps += "Update Z Row\n\n"
        self.LP.maximize = False
        self.coresimplex.solve()
        if(self.LP.tableau[0, self.LP.table_cols - 1] == 0 and self.LP.state == "optimal"):
             return True
        else :
            self.LP.state = "infeasible"
            return False
            

    def phase2(self):
         print("\n" + "=" * 60)
         print(" PHASE TWO  ".center(60))
         self.LP.steps += "PHASE TWO\n\n"
         print("=" * 60)
         print("\n")
         self.LP.phase1 = False
         z = [0] * self.LP.table_cols
         for i in range(len(self.input.zRow)):
             z[i]= -self.input.zRow[i]
        
         print("Insert Original Objective Function..........\n")
         self.LP.steps += "Insert Original Objective Function\n\n"
        
         for j in range(len(z)):
            self.LP.tableau[0, j] = z[j]
       
         self.coresimplex.DecorateSteps(self.LP)
           
      
         prevAritificalVariables ={}
         handledVar={}
         for index , var in enumerate(self.LP.variables):
            prevAritificalVariables[index]=0

        
         for a in self.atrificalVariables:
             if(a in self.LP.basic_variables): 
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
               handledVar[index-prevAritificalVariables[index]]=var
               if index in self.LP.basic_variables:
                  i= self.LP.basic_variables.index(index)
                  self.LP.basic_variables[i]=index-prevAritificalVariables[index]
               elif index in self.LP.non_basic_variables:
                  i= self.LP.non_basic_variables.index(index)
                  self.LP.non_basic_variables[i]=index-prevAritificalVariables[index]
         self.LP.variables = handledVar
       
          #      for j in range(self.LP.m):
        #          if(self.LP.basic_variables[j]==self.atrificalVariables[i]):
        #              self.LP.tableau.row_del(j+1)
        #              self.LP.table_rows-=1
        #              self.LP.m-=1
        #              self.LP.basic_variables.remove(self.atrificalVariables[i])
         
         print("Removing Atrifical Variables ..........\n")
         self.LP.steps += "Removing Atrifical Variables\n\n"
      
         self.coresimplex.DecorateSteps(self.LP)
         print("Update Z Row ..............\n")
         self.LP.steps += "Update Z Row\n\n"
        
         for i in range(len(self.LP.basic_variables)):
           
            factor = self.LP.tableau[0, self.LP.basic_variables[i]]
            
            if factor != 0:
                self.coresimplex.gaussJordan(self.LP.tableau,i+1,self.LP.basic_variables[i])
               
    
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
#)
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
input_data = Input( #reference !! done ☺️
      n=2,
      m=3,
      constraints=[
         Constrain([0.5, 0.25], "<=", 4, 1),
         Constrain([1, 3], ">=", 20, 1),
         Constrain([1, 1], "=", 10, 1)
      ],
      zRow=[2,3],maximize=False,isGoal=False,
      unrestricted=[False,False],
      symbol_map={0: "x1", 1: "x2"}
)

solver = TwoPhase(input_data)
solver.SetLinearProblem()

solver.solve()

