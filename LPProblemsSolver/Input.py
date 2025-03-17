from Constrain import Constrain

class Input:
    def __init__(self, n: int, m: int, constraints: list, zRow: list, maximize:bool, isGoal:bool,unrestricted:list,symbol_map:dict):
        self.n = n                   
        self.m = m                     
        self.constraints = constraints
        self.zRow = zRow              
        self.maximize = maximize      
        self.isGoal = isGoal    
        self.unrestricted=unrestricted      
        self.symbol_map=symbol_map
                

   