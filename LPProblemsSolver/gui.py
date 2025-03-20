import sys
from LPsolver import LPSolver
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QTabWidget, QTextEdit, QSpinBox,
                             QCheckBox, QScrollArea, QSizePolicy, QHeaderView, QFileDialog,
                             QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt
import numpy as np

# Your Input and Constraint classes
class Constrain:
    def __init__(self, coef, type, solution, priority):
        self.coef = coef       # list of coefficients
        self.type = type       # type of constraint >=, <=, =
        self.solution = solution  # rhs of constraint
        self.priority = priority  # priority of constraint if goal method

class Input:
    def __init__(self, n: int, m: int, constraints: list, zRow: list, maximize: bool, isGoal: bool, unrestricted: list, symbol_map: dict):
        self.n = n                  # number of variables          
        self.m = m                  # number of constraints         
        self.constraints = constraints  # constraints list
        self.zRow = zRow            # row of objective function      
        self.maximize = maximize    # max or minimize
        self.isGoal = isGoal        # is it goal or not
        self.unrestricted = unrestricted  # list of bool unrestricted is true
        self.symbol_map = symbol_map  # symbol map {0:x2,1:x1...xn}
        self.file = None            # file name

class LPSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Programming Solver")
        self.setMinimumSize(900, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        problem_tab = QWidget()
        solution_tab = QWidget()
        
        problem_layout = QVBoxLayout(problem_tab)
        solution_layout = QVBoxLayout(solution_tab)
        
        # Add tabs to tab widget
        tabs.addTab(problem_tab, "Problem Definition")
        tabs.addTab(solution_tab, "Solution")
        
        # Problem definition components
        self.setup_problem_tab(problem_layout)
        
        # Solution components
        self.setup_solution_tab(solution_layout)
        
        # Add tab widget to main layout
        main_layout.addWidget(tabs)
        
        # Set the central widget
        self.setCentralWidget(main_widget)
        
        # Store reference to the tabs
        self.tabs = tabs
        
        # Initialize some variables
        self.coefficient_table = None
        self.constraint_type_combos = []
        self.rhs_inputs = []
        self.priority_inputs = []
        self.unrestricted_checkboxes = []
    
    def setup_problem_tab(self, layout):
        # Method selection
        method_group = QGroupBox("Solution Method")
        method_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Standard Simplex", "BIG-M Method", "Two-Phase Method", "Goal Programming"])
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # Problem dimensions
        dimensions_group = QGroupBox("Problem Dimensions")
        dimensions_layout = QGridLayout()
        
        dimensions_layout.addWidget(QLabel("Number of Variables:"), 0, 0)
        self.var_count = QSpinBox()
        self.var_count.setRange(1, 100)
        self.var_count.setValue(2)
        dimensions_layout.addWidget(self.var_count, 0, 1)
        
        dimensions_layout.addWidget(QLabel("Number of Constraints:"), 1, 0)
        self.constraint_count = QSpinBox()
        self.constraint_count.setRange(1, 100)
        self.constraint_count.setValue(2)
        dimensions_layout.addWidget(self.constraint_count, 1, 1)
        
        # Objective function type
        dimensions_layout.addWidget(QLabel("Objective Function:"), 2, 0)
        self.objective_type = QComboBox()
        self.objective_type.addItems(["Maximize", "Minimize"])
        dimensions_layout.addWidget(self.objective_type, 2, 1)
        
        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)
        
        # Button to generate problem inputs
        generate_btn = QPushButton("Generate Problem Form")
        generate_btn.clicked.connect(self.generate_problem_form)
        layout.addWidget(generate_btn)
        
        # Scroll area for problem inputs
        self.problem_scroll = QScrollArea()
        self.problem_scroll.setWidgetResizable(True)
        self.problem_form = QWidget()
        self.problem_form_layout = QVBoxLayout(self.problem_form)
        self.problem_scroll.setWidget(self.problem_form)
        layout.addWidget(self.problem_scroll)
        
        # Solve button
        solve_btn = QPushButton("Solve")
        solve_btn.clicked.connect(self.solve_problem)
        layout.addWidget(solve_btn)
    
    def setup_solution_tab(self, layout):
        # Text area for solution output
        self.solution_output = QTextEdit()
        self.solution_output.setReadOnly(True)
        layout.addWidget(self.solution_output)
        
        # Save solution button
        save_btn = QPushButton("Save Solution")
        save_btn.clicked.connect(self.save_solution)
        layout.addWidget(save_btn)
    
    def on_method_changed(self, index):
        # Enable/disable goal programming specific fields
        is_goal = (index == 3)  # Index 3 is "Goal Programming"
        # Update visibility of priority fields (will be implemented when generating the form)
    
    def generate_problem_form(self):
        # Clear existing form
        while self.problem_form_layout.count():
            child = self.problem_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        n_vars = self.var_count.value()
        n_constraints = self.constraint_count.value()
        is_goal = self.method_combo.currentIndex() == 3  # Index 3 is "Goal Programming"
        
        # Create objective function inputs
        obj_group = QGroupBox("Objective Function")
        obj_layout = QGridLayout()
        
        # Objective function coefficients
        self.obj_coeffs = []
        for i in range(n_vars):
            obj_layout.addWidget(QLabel(f"x{i+1}:"), 0, i)
            coeff_input = QLineEdit("0")
            self.obj_coeffs.append(coeff_input)
            obj_layout.addWidget(coeff_input, 1, i)
        
        obj_group.setLayout(obj_layout)
        self.problem_form_layout.addWidget(obj_group)
        
        # Create constraints table
        constraints_group = QGroupBox("Constraints")
        constraints_layout = QVBoxLayout()
        
        self.coefficient_table = QTableWidget(n_constraints, n_vars)
        # Set headers
        headers = [f"x{i+1}" for i in range(n_vars)]
        self.coefficient_table.setHorizontalHeaderLabels(headers)
        # Set row numbers
        for i in range(n_constraints):
            self.coefficient_table.setVerticalHeaderItem(i, QTableWidgetItem(f"Constraint {i+1}"))
        
        # Initialize cells with zeros
        for row in range(n_constraints):
            for col in range(n_vars):
                self.coefficient_table.setItem(row, col, QTableWidgetItem("0"))
        
        constraints_layout.addWidget(self.coefficient_table)
        
        # Constraint types, RHS values, and priorities
        constraint_controls = QWidget()
        constraint_controls_layout = QGridLayout(constraint_controls)
        
        # Headers
        constraint_controls_layout.addWidget(QLabel("Type"), 0, 0)
        constraint_controls_layout.addWidget(QLabel("RHS"), 0, 1)
        if is_goal:
            constraint_controls_layout.addWidget(QLabel("Priority"), 0, 2)
        
        # Reset arrays
        self.constraint_type_combos = []
        self.rhs_inputs = []
        self.priority_inputs = []
        
        # Create input fields
        for i in range(n_constraints):
            # Constraint type
            type_combo = QComboBox()
            type_combo.addItems(["<=", ">=", "="])
            self.constraint_type_combos.append(type_combo)
            constraint_controls_layout.addWidget(type_combo, i+1, 0)
            
            # RHS value
            rhs_input = QLineEdit("0")
            self.rhs_inputs.append(rhs_input)
            constraint_controls_layout.addWidget(rhs_input, i+1, 1)
            
            # Priority (for goal programming)
            if is_goal:
                priority_input = QSpinBox()
                priority_input.setRange(1, n_constraints)
                priority_input.setValue(1)
                self.priority_inputs.append(priority_input)
                constraint_controls_layout.addWidget(priority_input, i+1, 2)
        
        constraints_layout.addWidget(constraint_controls)
        constraints_group.setLayout(constraints_layout)
        self.problem_form_layout.addWidget(constraints_group)
        
        # Unrestricted variables
        unrestricted_group = QGroupBox("Unrestricted Variables")
        unrestricted_layout = QHBoxLayout()
        
        self.unrestricted_checkboxes = []
        for i in range(n_vars):
            checkbox = QCheckBox(f"x{i+1}")
            self.unrestricted_checkboxes.append(checkbox)
            unrestricted_layout.addWidget(checkbox)
        
        unrestricted_group.setLayout(unrestricted_layout)
        self.problem_form_layout.addWidget(unrestricted_group)
    
    def solve_problem(self):
        try:
            # Collect all inputs
            n_vars = self.var_count.value()
            n_constraints = self.constraint_count.value()
            is_goal = self.method_combo.currentIndex() == 3
            maximize = self.objective_type.currentText() == "Maximize"
            
            # Get objective function coefficients
            z_row = []
            for coeff_input in self.obj_coeffs:
                z_row.append(float(coeff_input.text()))
            
            # Get constraints
            constraints = []
            for i in range(n_constraints):
                # Get coefficients
                coef = []
                for j in range(n_vars):
                    coef.append(float(self.coefficient_table.item(i, j).text()))
                
                # Get constraint type
                type_val = self.constraint_type_combos[i].currentText()
                
                # Get RHS
                solution = float(self.rhs_inputs[i].text())
                
                # Get priority (for goal programming)
                priority = 1
                if is_goal and i < len(self.priority_inputs):
                    priority = self.priority_inputs[i].value()
                
                constraints.append(Constrain(coef, type_val, solution, priority))
            
            # Get unrestricted variables
            unrestricted = [checkbox.isChecked() for checkbox in self.unrestricted_checkboxes]
            
            # Create symbol map
            symbol_map = {i: f"x{i+1}" for i in range(n_vars)}
            
            # Create Input object
            input_obj = Input(
                n=n_vars,
                m=n_constraints,
                constraints=constraints,
                zRow=z_row,
                maximize=maximize,
                isGoal=is_goal,
                unrestricted=unrestricted,
                symbol_map=symbol_map
            )
            
            # Call your solver here
            # For example: result = your_solver.solve(input_obj)
            solver = LPSolver()
            solver.input = input_obj
           
            
            result = solver.solve()
            
            # For now, we'll just display the input data for verification
            self.display_input_verification(result)
            
            # Switch to solution tab
            self.tabs.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def display_input_verification(self, input_obj):
        # This is a placeholder function to display the input data
        # In a real implementation, you would display the results from your solver
        output = "Input Verification:\n\n"
        
        output += f"Number of variables: {input_obj.n}\n"
        output += f"Number of constraints: {input_obj.m}\n"
        output += f"Objective function: {'Maximize' if input_obj.maximize else 'Minimize'}\n"
        output += f"Is goal programming: {'Yes' if input_obj.isGoal else 'No'}\n\n"
        
        output += "Objective function coefficients:\n"
        for i, coeff in enumerate(input_obj.zRow):
            output += f"x{i+1}: {coeff}\n"
        
        output += "\nConstraints:\n"
        for i, constraint in enumerate(input_obj.constraints):
            constraint_str = " + ".join([f"{coeff}*x{j+1}" for j, coeff in enumerate(constraint.coef) if coeff != 0])
            output += f"Constraint {i+1}: {constraint_str} {constraint.type} {constraint.solution}\n"
            if input_obj.isGoal:
                output += f"Priority: {constraint.priority}\n"
        
        output += "\nUnrestricted variables:\n"
        for i, unrestricted in enumerate(input_obj.unrestricted):
            output += f"x{i+1}: {'Unrestricted' if unrestricted else 'Non-negative'}\n"
        
        self.solution_output.setText(output)
    
    def save_solution(self):
        # Get the solution text
        solution_text = self.solution_output.toPlainText()
        
        # Open a file dialog to choose where to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Solution", "", "Text Files (*.txt);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(solution_text)
                QMessageBox.information(self, "Success", "Solution saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")


# Main function to run the application
def main():
    app = QApplication(sys.argv)
    window = LPSolverGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()