from Constrain import Constrain

class Input:
    def __init__(self, n: int, m: int, constraints, zRow, maximize, isGoal,unrestricted,symbol_map):
        self.n = n                   
        self.m = m                     
        self.constraints = constraints
        self.zRow = zRow              
        self.maximize = maximize      
        self.isGoal = isGoal    
        self.unrestricted=unrestricted      
        self.symbol_map=symbol_map
                

   