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
        pass    
    def gaussJordan(self,table:Matrix,row,col):
        pass
    def solve(self):
        pass
    def DecorateSteps(self):
        pass