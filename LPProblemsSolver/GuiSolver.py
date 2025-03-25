import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QTabWidget, QTextEdit, QSpinBox,
                             QCheckBox, QScrollArea, QSizePolicy, QHeaderView, QFileDialog,
                             QGridLayout, QMessageBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont
import numpy as np
# Import your solver modules
from Solver import Solver  
from TwoPhase import TwoPhase  
from BigM import BigM
from Input import Input
from Constrain import Constrain
from Goalprogramming import GoalProgramming
from Simplex import Simplex
from SubscriptSuperscriptLists import SubscriptSuperscriptLists

class LPSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Programming Solver")
        self.setMinimumSize(1000, 800)
        
        # Initialize the subscripts list
        self.subscribts = SubscriptSuperscriptLists()
        
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
        self.constraint_rows = []
        self.unrestricted_checkboxes = []
        self.method_choice = None
    
    def setup_problem_tab(self, layout):
        # Problem type selection
        problem_type_group = QGroupBox("Problem Type")
        problem_type_layout = QHBoxLayout()
        
        self.problem_type_radio = QButtonGroup()
        self.normal_lp_radio = QRadioButton("Normal LP")
        self.goal_lp_radio = QRadioButton("Goal Programming")
        self.normal_lp_radio.setChecked(True)
        
        self.problem_type_radio.addButton(self.normal_lp_radio)
        self.problem_type_radio.addButton(self.goal_lp_radio)
        
        # Connect the radio buttons to update UI
        self.normal_lp_radio.toggled.connect(self.update_problem_form)
        self.goal_lp_radio.toggled.connect(self.update_problem_form)
        
        problem_type_layout.addWidget(self.normal_lp_radio)
        problem_type_layout.addWidget(self.goal_lp_radio)
        
        problem_type_group.setLayout(problem_type_layout)
        layout.addWidget(problem_type_group)
        
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
        
        # Solver Method for >= or = constraints
        self.method_group = QGroupBox("Solver Method for >= or = Constraints")
        method_layout = QHBoxLayout()
        
        self.method_radio = QButtonGroup()
        self.bigm_radio = QRadioButton("BIG-M Method")
        self.two_phase_radio = QRadioButton("Two-Phase Method")
        self.bigm_radio.setChecked(True)
        
        self.method_radio.addButton(self.bigm_radio)
        self.method_radio.addButton(self.two_phase_radio)
        
        method_layout.addWidget(self.bigm_radio)
        method_layout.addWidget(self.two_phase_radio)
        
        self.method_group.setLayout(method_layout)
        layout.addWidget(self.method_group)
        
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
    
    def update_problem_form(self):
        # This will be called when the problem type radio changes
        # If we've already generated a form, regenerate it
        if hasattr(self, 'problem_form_layout') and self.problem_form_layout.count() > 0:
            self.generate_problem_form()
    
    def setup_solution_tab(self, layout):
        # Create a container widget to center the solution
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Text area for solution output with larger font
        self.solution_output = QTextEdit()
        self.solution_output.setReadOnly(True)
        font = QFont("Courier New", 12)  # Monospaced font for better table rendering
        self.solution_output.setFont(font)

        self.solution_output.setAlignment(Qt.AlignCenter)  # Center-align text
        
        # Add solution output to container with margins for centering
        container_layout.addWidget(self.solution_output)
        container_layout.setContentsMargins(10, 10, 10, 10)  # Add margins for visual centering
        
        # Add the container to the main layout
        layout.addWidget(container, 1)  # Use stretch factor for vertical centering
        
        # Save solution button
        save_btn = QPushButton("Save Solution")
        save_btn.clicked.connect(self.save_solution)
        layout.addWidget(save_btn, 0)  # No stretch
    
    def generate_problem_form(self):
        # Clear existing form
        while self.problem_form_layout.count():
            child = self.problem_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        n_vars = self.var_count.value()
        n_constraints = self.constraint_count.value()
        is_goal = self.goal_lp_radio.isChecked()
        
        # Create objective function inputs
        obj_group = QGroupBox("Objective Function")
        obj_layout = QGridLayout()
        
        # Objective function coefficients
        self.obj_coeffs = []
        for i in range(n_vars):
            var_symbol = self.subscribts.xlist[i] if i < len(self.subscribts.xlist) else f"x{i+1}"
            obj_layout.addWidget(QLabel(f"{var_symbol}:"), 0, i)
            coeff_input = QLineEdit("0")
            self.obj_coeffs.append(coeff_input)
            obj_layout.addWidget(coeff_input, 1, i)
        
        obj_group.setLayout(obj_layout)
        self.problem_form_layout.addWidget(obj_group)
        
        # Create constraints
        constraints_group = QGroupBox("Constraints")
        constraints_layout = QVBoxLayout()
        
        # Reset constraint rows
        self.constraint_rows = []
        
        # Create constraint rows with all elements on the same line
        for i in range(n_constraints):
            constraint_row = QWidget()
            row_layout = QHBoxLayout(constraint_row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # Label for constraint number
            row_layout.addWidget(QLabel(f"Constraint {i+1}:"))
            
            # Coefficients
            coefficient_inputs = []
            for j in range(n_vars):
                var_symbol = self.subscribts.xlist[j] if j < len(self.subscribts.xlist) else f"x{j+1}"
                
                # Create a small layout for each variable
                var_widget = QWidget()
                var_layout = QHBoxLayout(var_widget)
                var_layout.setContentsMargins(0, 0, 0, 0)
                var_layout.setSpacing(2)
                
                # Coefficient input
                coeff_input = QLineEdit("0")
                coeff_input.setFixedWidth(50)
                var_layout.addWidget(coeff_input)
                
                # Variable label
                var_layout.addWidget(QLabel(var_symbol))
                
                if j < n_vars - 1:
                    var_layout.addWidget(QLabel("+"))
                
                row_layout.addWidget(var_widget)
                coefficient_inputs.append(coeff_input)
            
            # Constraint type dropdown
            type_combo = QComboBox()
            type_combo.addItems(["<=", ">=", "="])
            type_combo.setFixedWidth(50)
            row_layout.addWidget(type_combo)
            
            # RHS value input
            rhs_input = QLineEdit("0")
            rhs_input.setFixedWidth(50)
            row_layout.addWidget(rhs_input)
            
            # Goal checkbox and priority input for goal programming
            is_goal_checkbox = None
            priority_input = None
            
            if is_goal:
                # Is Goal checkbox
                is_goal_checkbox = QCheckBox("Is Goal")
                is_goal_checkbox.setChecked(True)
                row_layout.addWidget(is_goal_checkbox)
                
                # Priority
                row_layout.addWidget(QLabel("Priority:"))
                priority_input = QSpinBox()
                priority_input.setRange(1, n_constraints)  # Allow any positive integer
                priority_input.setValue(n_constraints - i)
                row_layout.addWidget(priority_input)
            
            # Add spacer to push everything to the left
            row_layout.addStretch()
            
            # Store inputs for later retrieval
            self.constraint_rows.append({
                'coefficients': coefficient_inputs,
                'type': type_combo,
                'rhs': rhs_input,
                'is_goal': is_goal_checkbox,
                'priority': priority_input
            })
            
            constraints_layout.addWidget(constraint_row)
        
        constraints_group.setLayout(constraints_layout)
        self.problem_form_layout.addWidget(constraints_group)
        
        # Unrestricted variables
        unrestricted_group = QGroupBox("Unrestricted Variables")
        unrestricted_layout = QGridLayout()
        
        self.unrestricted_checkboxes = []
        # Arrange checkboxes in a grid (4 columns)
        col_count = 4
        for i in range(n_vars):
            var_symbol = self.subscribts.xlist[i] if i < len(self.subscribts.xlist) else f"x{i+1}"
            checkbox = QCheckBox(var_symbol)
            self.unrestricted_checkboxes.append(checkbox)
            row = i // col_count
            col = i % col_count
            unrestricted_layout.addWidget(checkbox, row, col)
        
        unrestricted_group.setLayout(unrestricted_layout)
        self.problem_form_layout.addWidget(unrestricted_group)
    
    def solve_problem(self):
        try:
            # Collect all inputs
            n_vars = self.var_count.value()
            n_constraints = self.constraint_count.value()
            is_goal_program = self.goal_lp_radio.isChecked()
            maximize = self.objective_type.currentText() == "Maximize"
            
            # Get objective function coefficients
            z_row = []
            for coeff_input in self.obj_coeffs:
                z_row.append(float(coeff_input.text()))
            
            # Get constraints
            constraints = []
            needs_advanced_solver = False

            for i, row in enumerate(self.constraint_rows):
                # Get coefficients
                coef = []
                for coeff_input in row['coefficients']:
                    coef.append(float(coeff_input.text()))
                
                # Get constraint type
                type_val = row['type'].currentText()
                if type_val in [">=", "="]:
                    needs_advanced_solver = True
                
                # Get RHS
                solution = float(row['rhs'].text())
                
                # Get priority (for goal programming)
                priority = 0
                if is_goal_program and row['priority']:
                    priority = row['priority'].value()
                
                # Check if this is a goal constraint
                is_goal = False
                if is_goal_program and row['is_goal']:
                    is_goal = row['is_goal'].isChecked()
                
                # Create constraint with isGoal attribute
                constraints.append(Constrain(coef, type_val, solution, priority, isGoal=is_goal))
            
            # Get unrestricted variables
            unrestricted = [checkbox.isChecked() for checkbox in self.unrestricted_checkboxes]
            
            # Create symbol map
            symbol_map = {}
            for i in range(n_vars):
                var_symbol = self.subscribts.xlist[i] if i < len(self.subscribts.xlist) else f"x{i+1}"
                symbol_map[i] = var_symbol
            
            # Create Input object
            input_obj = Input(
                n=n_vars,
                m=n_constraints,
                constraints=constraints,
                zRow=z_row,
                maximize=maximize,
                isGoal=is_goal_program,
                unrestricted=unrestricted,
                symbol_map=symbol_map
            )
           
            problem_input_str="Objective Function : "
            #  objective function
            obj_terms = []
            for j, coef in enumerate(z_row):
                if coef >= 0:
                    obj_terms.append(f"{coef}*{symbol_map[j]}")
                else:
                    obj_terms.append(f"- {abs(coef)}*{symbol_map[j]}")

            problem_input_str += " + ".join(obj_terms).replace("+ -", "- ") + "\n\nConstraints:\n"

            # Add constraints
            for i, constraint in enumerate(constraints, start=1):
                coef_terms = []
                for j, coef in enumerate(constraint.coef):
                    if coef >= 0:
                        coef_terms.append(f"{coef}*{symbol_map[j]}")
                    else:
                        coef_terms.append(f"- {abs(coef)}*{symbol_map[j]}")

                constraint_str = " + ".join(coef_terms).replace("+ -", "- ")
                full_constraint = f"{constraint_str} {constraint.type} {constraint.solution}"

                problem_input_str += f"{full_constraint}\n"


            unrestricted_vars = []
            for i in range(len(input_obj.unrestricted)):
                if input_obj.unrestricted[i]:
                    unrestricted_vars.append(f"x{i + 1}")

            if unrestricted_vars:
                problem_input_str += f"\nUnrestricted Variables: {', '.join(unrestricted_vars)}"
            else:
                problem_input_str += "\nAll variables are restricted."
            goal_status = " Goal Programming " if input_obj.isGoal else ""

            # Define whether it's a maximization or minimization problem
            optimization_type = "Maximization" if input_obj.maximize else "Minimization"

            # Start building the problem input string
            problem_input_str += f"{goal_status}\nOptimization Type: {optimization_type}\n\n "

            problem_input_str+="\n\n"
            input_obj.problemInput = problem_input_str
            print (problem_input_str)
            # Determine which solver to use based on constraint types and goal programming
            solver = None
            
            if is_goal_program:
                # Goal programming
                solver = GoalProgramming(input_obj)
            elif needs_advanced_solver:
                # If constraints contain >= or =, use BIG-M or Two-Phase
                if self.bigm_radio.isChecked():
                    solver = BigM(input_obj)
                else:
                    solver = TwoPhase(input_obj)
            else:
                # Standard Simplex for <= constraints
                solver = Simplex(input_obj)
            
            # Solve the problem
            if solver:
                solver.SetLinearProblem()
                solver.solve()
                solution_steps = solver.LP.steps
                
                # Display solution
                self.display_solution(solution_steps)
                
                # Switch to solution tab
                self.tabs.setCurrentIndex(1)
            else:
                QMessageBox.warning(self, "Warning", "No solver selected or constraints incompatible with method.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def display_solution(self, solution_steps):
        # Display the solution steps
        self.solution_output.setPlainText(solution_steps)
    
    def save_solution(self):
        # Get the solution text
        solution_text = self.solution_output.toPlainText()
        
        # Open a file dialog to choose where to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Solution", "", "Text Files (*.txt);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
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