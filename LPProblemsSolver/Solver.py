from abc import ABC, abstractmethod
from CoreSimplex import CoreSimplex
from LinearProblem import LinearProblem
from SubscriptSuperscriptLists import SubscriptSuperscriptLists
import Input as Input


class Solver(ABC):
    def __init__(self, input: Input):
        self.input = input
        self.LP = LinearProblem()
        self.LP.steps=input.problemInput
        self.coresimplex = CoreSimplex()
        self.subscribts = SubscriptSuperscriptLists()

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def SetLinearProblem(self):
        pass

    def printSolution(self):
        if self.LP.state != "optimal" and self.LP.state != "Goal" and self.LP.state != "Degeneracy":
            print(f"\n► Problem State: {self.LP.state.upper()}")
            self.LP.steps += f"\n► Problem State: {self.LP.state.upper()}\n\n"
            return

        print("\n" + "=" * 40)
        self.LP.steps += ("\n" + ("=" * 40))
        print(" SOLUTION SUMMARY ".center(40))
        self.LP.steps += "SOLUTION SUMMARY".center(18)
        print("=" * 40)
        self.LP.steps += "=" * 40+"\n"

        if not self.input.isGoal:
            value = str(self.LP.tableau[0, self.LP.table_cols-1])
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
                else:
                    value = round(value, 4)

            except (ValueError, TypeError):
                value = str(value)
            print(f"► Optimal Solution: {value}\n")
            self.LP.steps += f"\n► Optimal Solution: {value}\n\n"

        print("► Optimal Values:\n")
        self.LP.steps += "► Optimal Values:\n\n"
        x_lengths = [len(self.LP.variables[bv])
                     for bv in self.LP.basic_variables if self.LP.variables[bv].startswith("x")]
        max_var_length = max(x_lengths) if x_lengths else 10
        for i in self.LP.basic_variables:
            var = self.LP.variables[i]
            if var.startswith("x"):
                value = str(self.LP.tableau[self.LP.basic_variables.index(
                    i)+self.LP.objective_count, self.LP.table_cols-1])
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                    else:
                        value = round(value, 4)

                except (ValueError, TypeError):
                    value = str(value)
                if var.endswith("\u207A"):
                    var = var.replace("\u207A", "")
                    display_value = f"{value}"
                elif var.endswith("\u207B"):
                    var = var.replace("\u207B", "")
                    display_value = f"-{value}"
                else:
                    display_value = f"{value}"

                var_name = self.LP.variables.get(var, var)
                print(f"  {var_name.ljust(max_var_length)} : {display_value}")
                self.LP.steps += f"  {var_name.ljust(max_var_length)} : {display_value}\n"

        print(f"\n► Problem State: {self.LP.state.upper()}")
        self.LP.steps += f"\n► Problem State: {self.LP.state.upper()}\n\n"

        if self.input.isGoal:
            print("\n► Goal Analysis:")
            self.LP.steps += "\n► Goal Analysis:\n\n"
            k = 0
            r = 1
            for i, constraint in enumerate(self.input.constraints, start=1):
                coef_terms = []
                for j, coef in enumerate(constraint.coef):
                    if coef >= 0:
                        coef_terms.append(f"{coef}*{self.input.symbol_map[j]}")
                    else:
                        coef_terms.append(
                            f"- {abs(coef)}*{self.input.symbol_map[j]}")

                constraint_str = " + ".join(coef_terms).replace("+ -", "- ")
                full_constraint = f"{constraint_str} {constraint.type} {constraint.solution}"
                if constraint.isGoal:
                    status = "Satisfied" if self.LP.satisfied[k] else "Not Satisfied"
                    status_icon = "[✓]" if self.LP.satisfied[k] else "[✗]"
                    print(f"\nGoal {k+1}: {full_constraint}")
                    self.LP.steps += f"\nGoal {k+1}: {full_constraint}\n"
                    print(f"   {status_icon} {status}")
                    self.LP.steps += f"   {status_icon} {status}\n"
                    k = k+1
                elif not constraint.isGoal:
                    status = "Satisfied"
                    status_icon = "[✓]"
                    print(f"\nConstraint {r}: {full_constraint}")
                    self.LP.steps += f"\nConstrains {r}: {full_constraint}\n"
                    print(f"   {status_icon} {status}")
                    self.LP.steps += f"   {status_icon} {status}\n"
                    r = r+1
        print("\n" + "=" * 40 + "\n")
