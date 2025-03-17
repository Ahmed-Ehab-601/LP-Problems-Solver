import LinearProblem
import Input
from sympy import Matrix
class CoreSimplex:
    def __init__(self,input : Input = None,LP: LinearProblem = None):
        self.input = input # number of variables
        self.LP = LP # number of constraints
    def setLinearProblem(self):
        pass
    def getEntering(self,table:Matrix,row : int,col: int):
        pass
    def getLeaving(self,table:Matrix,max:bool,row : int,col: int):
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
                
            
        if leaving_varible==-1 :
            raise "Unbounded Solution"
        else : return leaving_varible
             
    def gaussJordan(self,table:Matrix,row,col):
        pass
    def solve(self):
        pass
    def DecorateSteps(self):
        pass