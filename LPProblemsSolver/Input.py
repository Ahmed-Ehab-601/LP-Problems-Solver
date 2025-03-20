from Constrain import Constrain

class Input:
    def __init__(self, n: int, m: int, constraints: list, zRow: list, maximize:bool, isGoal:bool,unrestricted:list,symbol_map:dict):
        self.n = n          #number of variables          
        self.m = m            #number of constraints         
        self.constraints = constraints #constraints list
        self.zRow = zRow        #row of objective function      
        self.maximize = maximize      #max or minimize
        self.isGoal = isGoal     # is it goal or not
        self.unrestricted=unrestricted  #list of bool unrestricted is true
        self.symbol_map=symbol_map #symbol map {0:x2,1:x1...xn}
        self.file = None        #file name
                

   