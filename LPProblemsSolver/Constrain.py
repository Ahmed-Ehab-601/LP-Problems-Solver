
class Constrain :
    def __init__(self,coef,type,solution,priority,isGoal=False):
        self.coef=coef #list of coff
        self.type=type #type of constrain >=,<=,=
        self.solution =solution #rhs of constrain
        self.priority= priority #priority of constrain if goal method
        self.isGoal=isGoal

   




