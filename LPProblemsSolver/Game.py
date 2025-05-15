from sympy import Matrix, pprint
from Input import Input
from Constrain import Constrain
import random
from SubscriptSuperscriptLists import SubscriptSuperscriptLists
from BigM import BigM
from TwoPhase import TwoPhase
class Game:
    def __init__(self, round_num = 0, player1_name="player1", player2_name="player2", N=2, is_player1_hider=True):
        self.round = round_num
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.num_of_places=N**2
        self.N = N
        self.is_player1_hider = is_player1_hider
        self.player1_prop = []
        self.player2_prop = []
        self.game_matrix =Matrix.zeros(N**2,N**2)
        self.world=Matrix.zeros(N,N)
    

    def randimazePlayer(self, player: int):
        if player == 1:
            non_zero_indices = [i for i, x in enumerate(self.tmp_player1_prop) if x != 0]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_player1_prop[random_index] -= self.smallest_element1
            else:
                self.tmp_player1_prop = self.player1_prop.copy()
                non_zero_indices = [i for i, x in enumerate(self.tmp_player1_prop) if x != 0]
                self.smallest_element1 = min(self.player1_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_player1_prop[random_index] -= self.smallest_element1
        else:
            non_zero_indices = [i for i, x in enumerate(self.tmp_player2_prop) if x != 0]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_player2_prop[random_index] -= self.smallest_element2
            else:
                self.tmp_player2_prop = self.player2_prop.copy()
                non_zero_indices = [i for i, x in enumerate(self.tmp_player2_prop) if x != 0]
                self.smallest_element2 = min(self.player2_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_player2_prop[random_index] -= self.smallest_element2

        i = random_index // self.N
        j = random_index % self.N
        return i, j


          
    def simulation(self):
        self.is_player1_hider=random.choice([True, False])   
        for i in range(10):
            row,col = self.randimazePlayer(1)
            if not self.is_player1_hider:
                row1 = row * self.N + col
            else :
                column1 = row * self.N + col
            row,col = self.randimazePlayer(2)
            if not self.is_player1_hider:   
                row1 = row * self.N + col
            else :
                column1 = row * self.N + col
            self.player1_score += self.game_matrix[row1, column1]
            self.player2_score -= self.game_matrix[row1, column1]
            
            self.print_world()


    def print_world(self):
        pprint(self.world)
        print("player 1 score: ")
        print(self.player1_score)
        print("vs player 2 score: ")
        print(self.player2_score)
        print("\n")
        print("player 1 prop: ")
        pprint(self.player1_prop)
        print("player 2 prop: ")
        pprint(self.player2_prop)

    def proximity(self):
        for i in range(self.N**2):
            row = i//self.N
            col = i%self.N
            # now we have choice let's pen it
            self.penalty(i,row,col-1,0.5)
            self.penalty(i,row,col+1,0.5)
            self.penalty(i,row-1,col,0.5)
            self.penalty(i,row+1,col,0.5)
            
            self.penalty(i,row,col-2,0.75)
            self.penalty(i,row,col+2,0.75)
            self.penalty(i,row-2,col,0.75)
            self.penalty(i,row+2,col,0.75)
            
            
            
    
    def penalty(self,place,row,col,factor):
        if col < 0 or col >= self.N or row < 0 or row >= self.N:
            return
        self.game_matrix[place,row*self.N+col] *= factor
        
                
    def build(self):
        for i in range(self.N):
            for j in range(self.N):
                difficulty = random.randint(1,3) # 1 = easy 2 = neutral  3 = hard
                self.world[i,j] = self.set_difficulty(difficulty)
                self.buildRow(i*self.N+j,difficulty)
                            
    def buildRow(self,row,difficulty):
        if difficulty == 1 : 
            self.game_matrix[row,:] = 2
            self.game_matrix[row,row] = -1
        elif difficulty == 2 :
            self.game_matrix[row,:] = 1
            self.game_matrix[row,row] = -1
        elif difficulty == 3 :
            self.game_matrix[row,:] = 1
            self.game_matrix[row,row] = -3
    
    def set_difficulty(self,difficulty):
        if difficulty == 1 : 
           return "E"
        elif difficulty == 2 :
            return "N"
        elif difficulty == 3 :
            return "H"
                                        
        
    def build_input_obj(self):
        constraints = []
        symbol_map = {}
      
        z_row = [0] * (self.num_of_places + 1)
        unrestricted = [False] * (self.num_of_places + 1)

        for i in range(self.num_of_places): 
            col = self.game_matrix[:,i]
            new_col = [-1 * x for x in col]
            new_col.append(1)
            print(new_col)
            constraints.append(Constrain(new_col, "<=", 0, 1))
            symbol_map[i] = f"x{i+1}"  
           
        last_constrain= [1] * self.num_of_places+ [0]
       
        constraints.append(Constrain(last_constrain, "=", 1, 1))
   
        z_row[self.num_of_places] = 1
        symbol_map[self.num_of_places]=f"x{self.num_of_places+1}" # For V
    
        unrestricted[self.num_of_places] = True
        
        input_data = Input(
            n=self.num_of_places+1,
            m=self.num_of_places + 1,
            constraints=constraints,
            zRow=z_row,
            maximize=True,
            isGoal=False,
            unrestricted=unrestricted,
            symbol_map=symbol_map

        )
        
        return input_data

    def calc_probability(self):
        solver = TwoPhase(self.build_input_obj())
        solver.SetLinearProblem()
    
        solver.solve()
        print(solver.LP.state)
        while(solver.LP.state!="optimal"):
            print(solver.LP.state)
            self.build()
            self.proximity()
            solver.solve()
            print("World",self.world)
            print("game matrix",self.game_matrix)
            print("player 1",self.player1_prop)
            print("player 2",self.player2_prop)
      
        z= solver.LP.tableau[0,:]
        z = z.subs(solver.LP.known_variables)
        print(z)
        start=self.num_of_places + 2
        for i in range(start,start+self.num_of_places):
            index=i-(start)
            self.player2_prop[index]=z[i]
        print(self.player2_prop)
        
        for i in solver.LP.basic_variables:
           name=solver.LP.variables[i]
           if name.startswith("x"):
              prob=solver.LP.tableau[solver.LP.basic_variables.index(i)+1, solver.LP.table_cols-1]
             
              if(i<self.num_of_places):
                  self.player1_prop[i]=prob
          
           print(self.player1_prop)
           print(self.player2_prop)

    def start_game(self):
        pass
    def human_turn(self):     
        pass

    def build_test(self):
        self.build()
        print(self.world)
        print(self.game_matrix)
        self.proximity()
        print(self.world)
        print(self.game_matrix)
          
game = Game()
game.start_game()        
