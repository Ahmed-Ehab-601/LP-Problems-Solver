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
        print("\n" + "=" * 40)
        print(" SOLUTION SUMMARY ".center(40))
        print("=" * 40)
        
        if not self.input.isGoal:
            print(f"\n► Optimal Solution: {self.LP.tableau[0, self.LP.table_cols-1]}\n")

        print("► Optimal Values:")
        max_var_length = max(len(self.LP.variables[bv]) for bv in self.LP.basic_variables if self.LP.variables[bv].startswith("x")) if self.LP.basic_variables else 10
        for i in self.LP.basic_variables:
            var=self.LP.variables[i]
            if var.startswith("x"):
                value = self.LP.tableau[self.LP.basic_variables.index(i)+self.LP.objective_count, self.LP.table_cols-1]
                if var == self.subscribts.xpluslist[i]:
                    display_value = f"{value}"
                elif var == self.subscribts.xminuslist[i]:
                    display_value = f"-{value}"
                else:
                    display_value = f"{value}"
               

                var_name = self.LP.variables.get(var, var)
                print(f"  {var_name.ljust(max_var_length)} : {display_value.rjust(10)}")

     
        print(f"\n► Problem State: {self.LP.state.upper()}")

       
        if self.input.isGoal:
            print("\n► Constraints Analysis:")
            k = 0
            for i, constraint in enumerate(self.input.constraints, start=1):
                coef_terms = []
                for j, coef in enumerate(constraint.coef):
                    if coef >= 0:
                        coef_terms.append(f"{coef}*{self.input.symbol_map[j]}")
                    else:
                        coef_terms.append(f"- {abs(coef)}*{self.input.symbol_map[j]}")
                
               
                constraint_str = " + ".join(coef_terms).replace("+ -", "- ")
                full_constraint = f"{constraint_str} {constraint.type} {constraint.solution}"
                if(constraint.type == "<="):
                      status = "Satisfied"
                      status_icon = "[✓]"
                else:
                     status = "Satisfied" if self.LP.satisfied[k] else "Not Satisfied"
                     status_icon = "[✓]" if self.LP.satisfied[k] else "[✗]"  
                     k+=1

               
                print(f"\nConstraint {i}: {full_constraint}")
                print(f"   {status_icon} {status}")
             

        print("\n" + "=" * 40 + "\n")