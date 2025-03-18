
from LinearProblem import LinearProblem
from SubscriptSuperscriptLists import SubscriptSuperscriptLists
from LinearProblem import LinearProblem
from tabulate import tabulate
from sympy import Matrix,pprint
class CoreSimplex:
    def __init__(self,LP: LinearProblem=None):
        if LP is not None:
            self.LP = LP
        else:
            self.LP = LinearProblem()
        self.subscribts = SubscriptSuperscriptLists()
    
    def getEntering(self,table:Matrix,max:bool,row : int,known_variables:dict = {}):
        z = table[row,:table.shape[1]-1].copy()
        if not max:
            z = -z
        z = z.subs(known_variables)
        min_num = min(z)
        index = list(z).index(min_num)
        if min_num == 0:
            return -1
        return index
      
    # row is index of last obj function (obj_count-1)
    def getLeaving(self,table:Matrix,row : int,col: int):
        pivot_col= table[:,col]
        rhs = table[:, -1]
        min_ratio=float('inf')
        leaving_varible=-1
        for i in range(row+1,table.shape[0]):
            ratio=None
            if pivot_col[i] >0 : 
                ratio = rhs[i]/pivot_col[i]
                if ratio<min_ratio:
                    min_ratio=ratio
                    leaving_varible=i 
        return leaving_varible
            
    def gaussJordan(self, table: Matrix, row, col):
        pivot = table[row, col]
        table[row, :] = table.row(row) / pivot 
        for i in range(table.rows):
            if i != row:
                coff = table[i, col]
                table[i, :] -= coff * table.row(row)
    def solve(self):
        if self.LP is None:
            return
        self.DecorateSteps(self.LP)
        cuurent_sol = None
        entering = self.getEntering(self.LP.tableau,self.LP.maximize,self.LP.objective_index,self.LP.known_variables)
        while entering != -1:
            if(self.LP.isGoal and not self.ckeckForCanSatisify()):
                self.LP.state = "Goal"
                break
            leaving = self.getLeaving(self.LP.tableau,self.LP.objective_count-1,entering)
            self.gaussJordan(self.LP.tableau, leaving, entering)
            new_sol = self.LP.tableau[self.LP.objective_index,self.LP.table_cols-1]
            if new_sol == cuurent_sol:
                self.LP.state = "Degeneracy"
                break
            else:
                cuurent_sol = new_sol
            col_leaving = self.LP.basic_variables[leaving-self.LP.objective_count]
            if leaving == -1:
                self.LP.state = "unbounded"
                break
            #swap col_leaving(basic) with entering(non basic)
            print(self.LP.variables[col_leaving],"Leaves <-> Enters",self.LP.variables[entering])
            print("")
            self.LP.steps += str(self.LP.variables[col_leaving])+" Leaves <-> Enters "+str(self.LP.variables[entering])+"\n\n"
            self.LP.basic_variables[leaving-self.LP.objective_count] = entering
            self.LP.non_basic_variables = [col_leaving if x == entering else x for x in self.LP.non_basic_variables]
            self.DecorateSteps(self.LP)
            entering = self.getEntering(self.LP.tableau,self.LP.maximize,self.LP.objective_index,self.LP.known_variables)
        if(entering == -1):
            self.LP.state = "optimal"
        return self.LP

    def ckeckForCanSatisify(self):
        entering = self.getEntering(self.LP.tableau,False,self.LP.objective_index,self.LP.known_variables)
        for i in range(self.LP.objective_count):
            if i == self.LP.objective_index:
                continue      
            if self.LP.tableau[i,entering] != 0 and self.LP.satisfied[i]:
                return False
        return True  
 
    def DecorateSteps(self,LP:LinearProblem):
        headers = ["Basic"] + [LP.variables[i] for i in LP.variables]  
        headers.append("RHS")  
        table_data = []
        for i in range(LP.objective_count):  
            if(LP.isGoal==False):
                z_row = ["Z" if not LP.phase1 else "r"] + list(self.LP.tableau[0, :]) 
            else: 
                z_row = [self.subscribts.zlist[i]] + list(LP.tableau[i, :]) 
            table_data.append(z_row)
       
        for i, row in enumerate(LP.tableau[LP.objective_count:, :].tolist()): 
            basic_var = LP.variables.get(LP.basic_variables[i], f"Var {LP.basic_variables[i]}")
            table_data.append([basic_var] + row)

        self.LP.steps += tabulate(table_data, headers=headers, tablefmt="grid")+'\n'+'\n'
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print("")

# def main():
#     #test get leaving
#    core = CoreSimplex()
#     tabel1 = Matrix([[1,-1,0,0,2,120],[0,-1/2,0,1,-0.5,10],[0,-0.5,1,0,1,30]])
#     print(core.getLeaving(tabel1,0,1))
#     tabel2 = Matrix([[-5,-4,0,0,0,0,0],[6,4,1,0,0,0,24],[1,2,0,1,0,0,6],[0,1,0,0,0,1,2]])
#     print(core.getLeaving(tabel2,0,0))
#     # #done
#     # #gauus jordan
#     matrix = Matrix([
#         [2, 1*'c', -1, 8], 
#         [-3, -1, 2, -11], 
#         [-2, 1, 2, -3]
#     ])

#     print("Original Matrix:")
#     print(matrix)
#     # Perform Gauss-Jordan elimination on row 0, column 1
#     core.gaussJordan(matrix, 0, 1)
#     print("\nTransformed Matrix (After Gauss-Jordan Elimination):")
#     print(matrix)
#     #done
#     #get entering
    # key = 'p'+"\u207A"
    # tabel1 = Matrix([[key,-1,0,0,2,120],[0,-1/2,0,1,-0.5,10],[0,-0.5,1,0,1,30]])
    # tabel1[0,0]*= -1
    # print(core.getEntering(tabel1,True,0,{key:9}))
    # tabel2 = Matrix([[-5,-4,0,0,0,0,0],[6,4,1,0,0,0,24],[1,2,0,1,0,0,6],[0,1,0,0,0,1,2]])
    # print(core.getEntering(tabel2,True,0,{'p':2}))
    #done

# if __name__ == "__main__":
#     main()