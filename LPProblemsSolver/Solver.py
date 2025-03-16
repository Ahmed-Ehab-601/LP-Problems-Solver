from abc import ABC, abstractmethod
import CoreSimplex
import LinearProblem
import Input
class Solver(ABC):
    def __init__(self, input:Input): 
        self.input = input
        self.LP = None
        self.coresimplex= CoreSimplex()   
    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def SetLinearProblem(self):
        pass
