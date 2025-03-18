from abc import ABC, abstractmethod
from CoreSimplex import CoreSimplex
from LinearProblem import LinearProblem
from SubscriptSuperscriptLists import SubscriptSuperscriptLists
import Input
class Solver(ABC):
    def __init__(self, input:Input): 
        self.input = input
        self.LP = LinearProblem()
        self.coresimplex= CoreSimplex()   
        self.subscribts = SubscriptSuperscriptLists()
    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def SetLinearProblem(self):
        pass
    
    def printSolution(self):
        #print state
        #handle print desision var
        #handle print objective if goal
        pass
        