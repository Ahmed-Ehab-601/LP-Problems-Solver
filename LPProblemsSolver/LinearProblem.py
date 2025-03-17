from sympy import Matrix

class LinearProblem:
    def __init__(self):
        self.n = None # number of variables
        self.m = None # number of constraints
        self.tableau = None # tableau initialization with Matrix.zeros(a,b)
        self.objective_index = 0 # objective index
        self.basic_variables = None  # basic variables
        self.non_basic_variables = None # non basic variables
        self.maximize = None
        self.variables = {} # variables map
        self.state = None # state of this optimal solution
        self.steps = None # steps
        self.objective_count = 1
        self.known_variables = {}
        self.isGoal = False
        self.table_rows = None
        self.table_cols = None
        
        
            
