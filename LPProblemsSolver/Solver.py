from abc import ABC, abstractmethod

class Solver(ABC):
    def __init__(self, input, Linearprogram,CoreSimplex): 
        self.input = input  
        self.LP = None
        self.coresimplex=None   
    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def SetLinearProblem(self):
        
        pass
