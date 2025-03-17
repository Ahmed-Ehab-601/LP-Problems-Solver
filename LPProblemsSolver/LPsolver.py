from Solver import Solver  
from TwoPhase import TwoPhase  
from BigM import BigM
from Input import Input
from Constrain import Constrain
class LPSolver:
    def __init__(self): 
      self.input = None
      self.solver = None 

    def check_constraints(self):
        for constraint in self.input.constraints:  
           if constraint in ['>=', '=']:  
               method = input("Enter which method to use (bigm, 2phase): ").lower()

               if method == 'bigm':
                   return BigM(self.input)  

               elif method == '2phase':
                   return TwoPhase(self.input)  

               else:
                   return None  
        pass
    def solve(self) :
       pass

    def get_input(self):
        n=int(input("Enter number of desction variables : "))
        m=int(input("Enter number of Constrains : "))
        goal = int(input("Enter 1 if Goal Programming or 0 if not: "))
        isGoal = True if goal == 1 else False

        symbol_map = {}
        input_map={}
        unrestricted = [False for i in range(n)]
        print("\n=== Objective Function ===\n")
        for i in range(n):
            symbol = input(f"Enter the symbol of decision variable {i + 1}: ")
            symbol_map[symbol] = i
            input_map[i]=symbol
            unres = input(f"If the decision variable {symbol} is unrestricted enter 1, if not enter 0: ")
            unrestricted[i] = True if unres == "1" else False
      
        zRow = []
        for symbol in symbol_map:
            coef = float(input(f"Enter coefficient of {symbol} in the objective function: "))
            zRow.append(coef)

        maximize_input = int(input("\nEnter 1 to maximize, 0 to minimize: "))
        maximize = True if maximize_input == 1 else False

        constraints = []
        print("\n=== Get Constrains ===\n")
        for i in range(m):
            coefs_input = input(f"Enter coefficients of constraint {i + 1}, separated by spaces: ")
            coefs = [float(x) for x in coefs_input.strip().split()]

            type_constraint = input(f"Enter type of constraint {i + 1} (<=, >=, =): ")
            solution = float(input("Enter the RHS value of the constraint: "))

            priority = 0
            if isGoal:
                priority = int(input(f"What is the priority of constraint {i + 1}? "))

            constraint = Constrain(coefs, type_constraint, solution, priority)
            constraints.append(constraint)
        
        self.input = Input(n, m, constraints, zRow, maximize, isGoal,unrestricted,input_map)
        print("\n=== INPUT SUMMARY ===\n")
        print("Objective Function (Z Row):")
        for i, coef in enumerate(zRow):
            var_symbol = input_map[i]
            print(f"  {coef} * {var_symbol}")

        print("\nDecision Variables:")
        for idx, symbol in input_map.items():
            unrestricted_status = "Unrestricted" if unrestricted[idx] else "Restricted (>= 0)"
            print(f"  {symbol}: {unrestricted_status}")

        print(f"\nOptimization Goal: {'Maximize' if maximize else 'Minimize'}")

        print("\nConstraints:")
        for i, constraint in enumerate(constraints, start=1):
            coefs_str = " + ".join([f"{coef} * {input_map[j]}" for j, coef in enumerate(constraint.coef)])
            goal_priority = f", Priority: {constraint.priority}" if isGoal else ""
            print(f"  Constraint {i}: {coefs_str} {constraint.type} {constraint.solution}{goal_priority}")

        print("\nUnrestricted Variables:")
        for i, is_unrestricted in enumerate(unrestricted):
            if is_unrestricted:
                print(f"  {input_map[i]} is unrestricted.")

        print("\nSymbol Map (Variable to Index):")
        for idx, symbol in input_map.items():
            print(f"  {symbol} -> Index {idx}")

        print("\n=== END OF INPUT SUMMARY ===\n")

# l=LPSolver()
# l.get_input()
