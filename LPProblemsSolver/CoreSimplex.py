import LinearProblem
import Input
from sympy import Matrix,pprint
class CoreSimplex:
    def __init__(self,LP: LinearProblem=None):
        self.LP = LP
        
    
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
        pass
    def DecorateSteps(self):
        pass
    
def main():
    #test get leaving
    core = CoreSimplex()
    tabel1 = Matrix([[1,-1,0,0,2,120],[0,-1/2,0,1,-0.5,10],[0,-0.5,1,0,1,30]])
    print(core.getLeaving(tabel1,0,1))
    tabel2 = Matrix([[-5,-4,0,0,0,0,0],[6,4,1,0,0,0,24],[1,2,0,1,0,0,6],[0,1,0,0,0,1,2]])
    print(core.getLeaving(tabel2,0,0))
    # #done
    # #gauus jordan
    matrix = Matrix([
        [2, 1*'c', -1, 8], 
        [-3, -1, 2, -11], 
        [-2, 1, 2, -3]
    ])

    print("Original Matrix:")
    print(matrix)
    # Perform Gauss-Jordan elimination on row 0, column 1
    core.gaussJordan(matrix, 0, 1)
    print("\nTransformed Matrix (After Gauss-Jordan Elimination):")
    print(matrix)
    #done
    #get entering
    tabel1 = Matrix([[1*'p',-1,0,0,2,120],[0,-1/2,0,1,-0.5,10],[0,-0.5,1,0,1,30]])
    print(core.getEntering(tabel1,False,0,{'p':1}))
    tabel2 = Matrix([[-5,-4,0,0,0,0,0],[6,4,1,0,0,0,24],[1,2,0,1,0,0,6],[0,1,0,0,0,1,2]])
    print(core.getEntering(tabel2,False,0,{'p':2}))
    #done
    

    

    
   

if __name__ == "__main__":
    main()