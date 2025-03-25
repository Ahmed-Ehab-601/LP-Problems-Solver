from sympy import Matrix


class LinearProblem:
    def __init__(self):
        self.n = None  # number of variables
        self.m = None  # number of constraints
        self.tableau = None  # tableau initialization with Matrix.zeros(a,b)
        self.objective_index = 0  # objective index
        self.basic_variables = []  # basic variables
        self.non_basic_variables = []  # non basic variables
        self.maximize = None  # max or min
        self.variables = {}  # variables map
        self.state = None  # state of this optimal solution
        self.steps = ""  # steps
        self.objective_count = 1  # objective count
        self.known_variables = {}  # known variables
        self.isGoal = False  # is goal 
        self.table_rows = None  # number of table rows
        self.table_cols = None  # number of table cols
        self.goal_map = {}  # goal map
        self.goal_values = []  # goal values
        self.satisfied = []  # satisfied goals
        self.phaseOne = False  # is in phase one
        self.needPhaseOne = False  # need phase one
