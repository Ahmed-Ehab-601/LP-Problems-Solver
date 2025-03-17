from Solver import Solver
from LinearProblem import LinearProblem
from sympy import Matrix, pprint
from Constrain import Constrain
from Input import Input
from CoreSimplex import CoreSimplex

class TwoPhase(Solver):
    atrificalVariables=[]
    def SetLinearProblem(self):
        self.LP = LinearProblem()
        self.LP.n = self.input.n
        self.LP.m = self.input.m
        self.LP.variables = self.input.symbol_map.copy()
        self.LP.basic_variables = [None] * self.LP.m 
        self.LP.tableau = self.get_table()
        pprint(self.LP.tableau)
        print(self.LP.basic_variables)
        print(self.atrificalVariables)
        self.coresimplex=CoreSimplex(self.LP)

    def solve(self):
        if self.phase1():
            if self.phase2():
                return

    def get_table(self):
        num_artificiale = 0
        for constraint in self.input.constraints:
            if constraint.type == ">=" or constraint.type == "=":
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
                    m[i, self.LP.n+j] = -1 * constraint.coef[j]
                    self.LP.variables[self.LP.n+j] = "-" + str(self.LP.variables[j])
                  
                   
                
            if constraint.type == "<=":
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1]=self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = "s" + str(i)
                slack+=1

            elif constraint.type == ">=":
                m[i,self.LP.n+slack+num_unRes] = -1
                self.LP.variables[self.LP.n+slack+num_unRes] = "e" + str(i)
                slack+=1
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1] =self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = "a" + str(i)
                self.atrificalVariables.append(self.LP.n+slack+num_unRes)
                z_artificial[self.LP.n+slack+num_unRes] = -1
                slack+=1
           

            elif constraint.type == "=":
                m[i,self.LP.n+slack+num_unRes] = 1
                self.LP.basic_variables[i - 1] = self.LP.n+slack+num_unRes
                self.LP.variables[self.LP.n+slack+num_unRes] = "a" + str(i)
                self.atrificalVariables.append(self.LP.n+slack+num_unRes)
                z_artificial[self.LP.n+slack+num_unRes] = -1
                slack += 1

            m[i, self.LP.table_cols - 1] = constraint.solution
            i += 1
     

        for j in range(len(z_artificial)):
            m[0, j] = z_artificial[j]
      
        return m

    def phase1(self):
        for i in range(self.LP.m):
            factor = self.LP.tableau[0, self.LP.basic_variables[i]]
            if factor != 0:
                self.LP.tableau[0, :] -= factor * self.LP.tableau[i + 1, :]
        self.coresimplex.solve()
        if(self.LP.tableau[0, self.LP.table_cols - 1] == 0):
             return True
        else :
             return False
            

    def phase2(self):
         for i in range(len(self.atrificalVariables)):# Remove Cols 
             self.LP.tableau.col_del(self.atrificalVariables[i])
             self.LP.table_cols-=1
             for j in range(self.LP.m):
                 if(self.LP.basic_variables[j]==self.atrificalVariables[i]):
                     self.LP.tableau.row_del(j+1)
                     self.LP.table_rows-=1
                     self.LP.basic_variables.remove(self.atrificalVariables[i])
        
         z = [0] * self.LP.table_cols
         for i in range(len(self.input.zRow)):
             z[i]=self.input.zRow[i]
         self.LP.tableau[0]=z  
         for i in range(self.LP.m):
            factor = self.LP.tableau[0, self.LP.basic_variables[i]]
            if factor != 0:
                self.coresimplex.gaussJordan(self.LP.tableau,i+1,self.LP.basic_variables[i])
         self.coresimplex.solve()
              


constraints = [
    Constrain([1, 3], "<=", 5, 1),
    Constrain([5, 6], ">=", 10, 1)
]

input_data = Input(
    n=2,
    m=2,
    constraints=constraints,
    zRow=[1, 1],
    maximize=True,   
    isGoal=False,  
    unrestricted=[True, True],
    symbol_map={0: "x", 1: "y"}
)

solver = TwoPhase(input_data)
solver.SetLinearProblem()
