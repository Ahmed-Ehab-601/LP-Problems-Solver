from abc import ABC, abstractmethod
from CoreSimplex import CoreSimplex
from LinearProblem import LinearProblem
import Input
class Solver(ABC):
    def __init__(self, input:Input): 
        self.input = input
        self.LP = LinearProblem()
        self.coresimplex= CoreSimplex()   
    @abstractmethod
    def solve(self):
        
        pass

    @abstractmethod
    def SetLinearProblem(self):
        pass
    