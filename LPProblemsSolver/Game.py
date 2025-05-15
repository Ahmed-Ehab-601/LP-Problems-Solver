from sympy import Matrix, pprint
import random

from scipy.optimize import linprog
import numpy as np
class Game:
    def __init__(self, round_num = 0, player1_name="player1", player2_name="player2", N=4, is_player1_hider=True):
        self.round = round_num
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.num_of_places=N**2
        self.N = N
        self.is_player1_hider = is_player1_hider
        self.game_matrix = np.zeros((self.num_of_places,self.num_of_places))
        
        self.world = np.full((N,N),"",dtype=str)
        self.player1_prop=[0]*self.num_of_places
        self.player2_prop=[0]*self.num_of_places
        self.tmp_player1_prop = [0]*self.num_of_places
        self.tmp_player2_prop = [0]*self.num_of_places
        self.smallest_element1 = 0
        self.smallest_element2 = 0
        self.game_value = 0
    
    def randimazePlayer(self, player: int):
        if player == 1:
            non_zero_indices = [i for i, x in enumerate(self.tmp_player1_prop) if x >= self.smallest_element1]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_player1_prop[random_index] -= self.smallest_element1
                self.tmp_player1_prop = [round(x, 6) for x in self.tmp_player1_prop]
            else:
                a = np.array(self.player1_prop)
                b = np.array(self.tmp_player1_prop)
                self.tmp_player1_prop = (a+b).tolist()
                non_zero_indices = [i for i, x in enumerate(self.tmp_player1_prop) if x >= self.smallest_element1]
                self.smallest_element1 = min(self.player1_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_player1_prop[random_index] -= self.smallest_element1
        else:
            non_zero_indices = [i for i, x in enumerate(self.tmp_player2_prop) if x >= self.smallest_element2]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_player2_prop[random_index] -= self.smallest_element2
                self.tmp_player2_prop = [round(x, 6) for x in self.tmp_player2_prop]
            else:
                a = np.array(self.player2_prop)
                b = np.array(self.tmp_player2_prop)
                self.tmp_player2_prop = (a+b).tolist()
                non_zero_indices = [i for i, x in enumerate(self.tmp_player2_prop) if x >= self.smallest_element2]
                self.smallest_element2 = min(self.player2_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_player2_prop[random_index] -= self.smallest_element2

        i = random_index // self.N
        j = random_index % self.N
        return i, j


    def print_world(self):
        pprint(self.world)
        print("player 1 score: ")
        print(self.player1_score)
        print("vs player 2 score: ")
        print(self.player2_score)
        print("\n")
        print("player 1 prop: ")
        pprint(self.tmp_player1_prop)
        print("player 2 prop: ")
        pprint(self.tmp_player2_prop)      
    def simulation(self):
        self.is_player1_hider=random.choice([True, False])   
        for i in range(100):
            row,col = self.randimazePlayer(1)
            print("player 1 turn",row,col)
            if  self.is_player1_hider:
                row1 = row * self.N + col
            else :
                column1 = row * self.N + col
            row,col = self.randimazePlayer(2)
            print("player 2 turn",row,col)
            if not self.is_player1_hider:   
                row1 = row * self.N + col
            else :
                column1 = row * self.N + col
            if self.is_player1_hider: 
                self.player1_score += self.game_matrix[row1, column1]
                self.player2_score -= self.game_matrix[row1, column1]   
            else:
                self.player1_score -= self.game_matrix[row1, column1]
                self.player2_score += self.game_matrix[row1, column1]
            
            self.print_world()
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
                                        
        
    def build_constraint(self,type:str):
        # We'll replace this with code that builds matrices for scipy.optimize.linprog
        # Instead of returning a custom Input object
        
        # For player 1's strategy, we want to maximize v subject to:
        # -A^T x + v ≤ 0
        # sum(x) = 1
        # x ≥ 0
        
        # Set up the coefficient matrix for constraints
        # Each column in game_matrix becomes a row constraint
        A_ub = np.zeros((self.num_of_places, self.num_of_places + 1))
        
        # Fill A_ub with the negated transpose of game_matrix
        for i in range(self.num_of_places):
            if(type == "x"):
                 A_ub[i, :self.num_of_places] = -1 * self.game_matrix[:, i]
            else:
                 A_ub[i, :self.num_of_places] = -1 * self.game_matrix[i, :]     
           
            A_ub[i, self.num_of_places] = 1  # Coefficient for v
        
        # RHS of inequality constraints
        b_ub = np.zeros(self.num_of_places)
        
        # Equality constraint: sum of probabilities = 1
        A_eq = np.zeros((1, self.num_of_places + 1))
        A_eq[0, :self.num_of_places] = 1  # Sum of probabilities
        A_eq[0, self.num_of_places] = 0   # v doesn't participate in this constraint
        b_eq = np.array([1])  # Sum equals 1
        
        # Objective: maximize v (or minimize -v)
        # All other variables have 0 coefficient in objective
        c = np.zeros(self.num_of_places + 1)
        c[self.num_of_places] = -1  # Negative because linprog minimizes
        
        # Bounds: x_i ≥ 0, v is unrestricted
        bounds = [(0, None) for _ in range(self.num_of_places)] + [(None, None)]
        
        return {
            'c': c,
            'A_ub': A_ub,
            'b_ub': b_ub,
            'A_eq': A_eq,
            'b_eq': b_eq,
            'bounds': bounds
        }
            
    def calc_probability(self):
        # Get the LP parameters
        x_input = self.build_constraint("x")   
        x_result = linprog(
            c=x_input['c'],
            A_ub=x_input['A_ub'],
            b_ub=x_input['b_ub'],
            A_eq=x_input['A_eq'],
            b_eq=x_input['b_eq'],
            bounds=x_input['bounds'],
            method='highs'  # Using HiGHS solver which is more modern and reliable
        )
        
        y_input = self.build_constraint("y")   
        y_result = linprog(
            c=x_input['c'],
            A_ub=y_input['A_ub'],
            b_ub=y_input['b_ub'],
            A_eq=y_input['A_eq'],
            b_eq=y_input['b_eq'],
            bounds=y_input['bounds'],
            method='highs'
        )
        
        print(f"Optimization status: {x_result.message}")
        print(f"Optimization status: {y_result.message}")
        
        # Extract solution
        if x_result.success:
            # Store the optimal mixed strategy for player 1
            self.player1_prop = x_result.x[:self.num_of_places]
            self.player2_prop = y_result.x[:self.num_of_places]
            
            non_zero_indices = [i for i, x in enumerate(self.player1_prop) if x != 0]
            self.smallest_element1 = min(self.player1_prop[i] for i in non_zero_indices)
            
            non_zero_indices = [i for i, x in enumerate(self.player2_prop) if x != 0]
            self.smallest_element2 = min(self.player2_prop[i] for i in non_zero_indices)
            
            # The optimal value of the game is the negative of the objective value 
            # (since we minimized -v)
            self.game_value = -x_result.fun
            
            # 0.4 0.1 0.3 0.2
            
            #4
            
        
        else:
            print("Failed to find optimal strategy")

    def start_game(self):
        self.build()
        self.proximity()
        self.calc_probability()
        print("World",self.world)
        print("game matrix",self.game_matrix)
        print("player 1",self.player1_prop)
        print("player 2",self.player2_prop)
        print(f"Game value: {self.game_value}")

    def human_turn(self, i, j):
        if self.is_player1_hider:
            row1 = i * self.N + j
        else:
            column1 = i * self.N + j

        non_zero_indices = [idx for idx, x in enumerate(self.tmp_player1_prop) if x >= self.smallest_element1]
        if non_zero_indices:
            if self.is_player1_hider and row1 in non_zero_indices:
                self.tmp_player1_prop[row1] -= self.smallest_element1
            elif not self.is_player1_hider and column1 in non_zero_indices:
                self.tmp_player1_prop[column1] -= self.smallest_element1
            self.tmp_player1_prop = [round(x, 6) for x in self.tmp_player1_prop]
        else:
            a = np.array(self.player1_prop)
            b = np.array(self.tmp_player1_prop)
            self.tmp_player1_prop = (a+b).tolist().copy()
            non_zero_indices = [idx for idx, x in enumerate(self.tmp_player1_prop) if x >= self.smallest_element1]
            self.smallest_element1 = min(self.player1_prop[i] for i in non_zero_indices)
            if self.is_player1_hider and row1 in non_zero_indices:
                self.tmp_player1_prop[row1] -= self.smallest_element1
            elif not self.is_player1_hider and column1 in non_zero_indices:
                self.tmp_player1_prop[column1] -= self.smallest_element1

        row, col = self.randimazePlayer(2)
        if not self.is_player1_hider:
            row1 = row * self.N + col
        else:
            column1 = row * self.N + col

        self.player1_score += self.game_matrix[row1, column1]
        self.player2_score -= self.game_matrix[row1, column1]
        self.print_world()
    def build_test(self):
        self.build()
        print(self.world)
        print(self.game_matrix)
        self.proximity()
        print(self.world)
        print(self.game_matrix)
          
game = Game()
game.start_game() 
game.simulation()

# game.human_turn(0,0)
# game.human_turn(0,1)
# game.human_turn(1,0)
# game.human_turn(1,1)
