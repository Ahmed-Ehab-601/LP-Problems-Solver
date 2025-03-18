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
        k=0
        if not self.input.isGoal:
            print(f"Solution : {self.LP.tableau[0,self.LP.table_cols-1]}")
        for i in range(len(self.LP.basic_variables)):
            print(f"{self.LP.variables[self.LP.basic_variables[i]] }: {self.LP.tableau[i+1,self.LP.table_cols-1]}")
        print(f"With Problem State : {self.LP.state}")
        if self.input.isGoal:
            for i, constraint in enumerate(self.input.constraints, start=1):
                if(constraint.type == ">="):
                    coefs_str = " + ".join([f"{coef} * {self.input.symbol_map[j]}" for j, coef in enumerate(constraint.coef)])
                    goal_priority = f", Saitsfied:" if self.LP.satisfied[k] else ", Not Saitsfied"
                    print(f"Constraint {i}: {coefs_str} {constraint.type} {constraint.solution}{goal_priority}")
                    k+=1

                
