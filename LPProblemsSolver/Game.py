import numpy as np
import random
from scipy.optimize import linprog
from tabulate import tabulate

class Game:
    def __init__(self, round_num=0, player1_name="Human", player2_name="Computer", N=4, is_player1_hider=True):
        self.round = round_num
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.player1_rounds_won = 0
        self.player2_rounds_won = 0
        self.num_of_places = N**2
        self.N = N
        self.is_player1_hider = is_player1_hider
        self.game_matrix = np.zeros((self.num_of_places, self.num_of_places))
                
        self.world = np.full((N, N), "", dtype=str)
        self.x_prop = [0]*self.num_of_places
        self.y_prop = [0]*self.num_of_places
        self.tmp_x_prop = [0]*self.num_of_places
        self.tmp_y_prop = [0]*self.num_of_places
        self.smallest_elementx = 0
        self.smallest_elementy = 0
        self.game_value = 0
        
        # For tracking the last moves
        self.last_human_move = None
        self.last_computer_move = None
        self.last_round_winner = None
    
    def randimazePlayer(self, player: int):
        if player == 1:
            non_zero_indices = [i for i, x in enumerate(self.tmp_x_prop) if x >= self.smallest_elementx]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_x_prop[random_index] -= self.smallest_elementx
                self.tmp_x_prop = [round(x, 6) for x in self.tmp_x_prop]
            else:
                a = np.array(self.x_prop)
                b = np.array(self.tmp_x_prop)
                self.tmp_x_prop = (a+b).tolist()
                non_zero_indices = [i for i, x in enumerate(self.tmp_x_prop) if x >= self.smallest_elementx]
                self.smallest_elementx = min(self.x_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_x_prop[random_index] -= self.smallest_elementx
        else:
            non_zero_indices = [i for i, x in enumerate(self.tmp_y_prop) if x >= self.smallest_elementy]
            if non_zero_indices:
                random_index = random.choice(non_zero_indices)
                self.tmp_y_prop[random_index] -= self.smallest_elementy
                self.tmp_y_prop = [round(x, 6) for x in self.tmp_y_prop]
            else:
                a = np.array(self.y_prop)
                b = np.array(self.tmp_y_prop)
                self.tmp_y_prop = (a+b).tolist()
                non_zero_indices = [i for i, x in enumerate(self.tmp_y_prop) if x >= self.smallest_elementy]
                self.smallest_elementy = min(self.y_prop[i] for i in non_zero_indices)
                random_index = random.choice(non_zero_indices)
                self.tmp_y_prop[random_index] -= self.smallest_elementy

        i = random_index // self.N
        j = random_index % self.N
        return i, j

    def proximity(self):
        for i in range(self.N**2):
            row = i//self.N
            col = i%self.N
            # now we have choice let's pen it
            self.penalty(i, row, col-1, 0.5)
            self.penalty(i, row, col+1, 0.5)
            self.penalty(i, row-1, col, 0.5)
            self.penalty(i, row+1, col, 0.5)
            
            self.penalty(i, row, col-2, 0.75)
            self.penalty(i, row, col+2, 0.75)
            self.penalty(i, row-2, col, 0.75)
            self.penalty(i, row+2, col, 0.75)
            
            self.penalty(i, row+1, col+1, 0.75)
            self.penalty(i, row+1, col-1, 0.75)
            self.penalty(i, row-1, col+1, 0.75)
            self.penalty(i, row-1, col-1, 0.75)
            
            
    
    def penalty(self, place, row, col, factor):
        if col < 0 or col >= self.N or row < 0 or row >= self.N:
            return
        self.game_matrix[place, row*self.N+col] *= factor
        
    def build(self):
        for i in range(self.N):
            for j in range(self.N):
                difficulty = random.randint(1, 3)  # 1 = easy 2 = neutral  3 = hard
                self.world[i, j] = self.set_difficulty(difficulty)
                self.buildRow(i*self.N+j, difficulty)
    
    def test_build(self):
        for i in range(self.N):
            for j in range(self.N):
                difficulty = self.get_difficulty(self.world[i, j])  # 1 = easy 2 = neutral  3 = hard
                self.buildRow(i*self.N+j, difficulty)            
                            
    def buildRow(self, row, difficulty):
        if difficulty == 1:  # Easy
            self.game_matrix[row, :] = 2
            self.game_matrix[row, row] = -1
        elif difficulty == 2:  # Neutral
            self.game_matrix[row, :] = 1
            self.game_matrix[row, row] = -1
        elif difficulty == 3:  # Hard
            self.game_matrix[row, :] = 1
            self.game_matrix[row, row] = -3
    
    def set_difficulty(self, difficulty):
        if difficulty == 1: 
            return "E"  # Easy
        elif difficulty == 2:
            return "N"  # Neutral
        elif difficulty == 3:
            return "H"  # Hard
    
    def get_difficulty(self, difficulty):
        if difficulty == "E": 
            return 1  # Easy
        elif difficulty == "N":
            return 2  # Neutral
        elif difficulty == "H":
            return 3  # Hard    
                                        
    def build_constraint(self, type: str):
        # Set up the coefficient matrix for constraints
        A_ub = np.zeros((self.num_of_places, self.num_of_places + 1))
        
        # Fill A_ub with the negated transpose of game_matrix
        for i in range(self.num_of_places):
            if(type == "x"):
                 A_ub[i, :self.num_of_places] = -1 * self.game_matrix[:, i]
                 A_ub[i, self.num_of_places] = 1  # Coefficient for v
            else:
                 A_ub[i, :self.num_of_places] = 1 * self.game_matrix[i, :]
                 A_ub[i, self.num_of_places] = -1  # Coefficient for v
            
        
        # RHS of inequality constraints
        b_ub = np.zeros(self.num_of_places)
        
        # Equality constraint: sum of probabilities = 1
        A_eq = np.zeros((1, self.num_of_places + 1))
        A_eq[0, :self.num_of_places] = 1  # Sum of probabilities
        A_eq[0, self.num_of_places] = 0   # v doesn't participate in this constraint
        b_eq = np.array([1])  # Sum equals 1
        
        # Objective: maximize v (or minimize -v)
        c = np.zeros(self.num_of_places + 1)
        
        if(type == "x"):
            c[self.num_of_places] = -1  # Negative because linprog minimizes
        else:
            c[self.num_of_places] = 1  
        
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
            c=y_input['c'],
            A_ub=y_input['A_ub'],
            b_ub=y_input['b_ub'],
            A_eq=y_input['A_eq'],
            b_eq=y_input['b_eq'],
            bounds=y_input['bounds'],
            method='highs'
        )
        
        # Extract solution
        if x_result.success and y_result.success:
            # Store the optimal mixed strategy for players
            self.x_prop = x_result.x[:self.num_of_places]
            self.y_prop = y_result.x[:self.num_of_places]
            
            non_zero_indices = [i for i, x in enumerate(self.x_prop) if x != 0]
            self.smallest_elementx = min(self.x_prop[i] for i in non_zero_indices) if non_zero_indices else 0
            
            non_zero_indices = [i for i, x in enumerate(self.y_prop) if x != 0]
            self.smallest_elementy = min(self.y_prop[i] for i in non_zero_indices) if non_zero_indices else 0
            
            # The optimal value of the game is the negative of the objective value
            self.game_value = -x_result.fun
            
            self.tmp_x_prop = self.x_prop.copy()
            self.tmp_y_prop = self.y_prop.copy()
            
            return True
        else:
            print("Failed to find optimal strategy")
            return False

    def start_game(self):
        self.build()
        self.proximity()
        return self.calc_probability()

    def human_turn(self, i, j):
      # Record human move
        self.last_human_move = (i, j)
      # Convert 2D coordinates to 1D index
        human_index = i * self.N + j
      # Determine if human is hider or seeker and set appropriate indices
        if self.is_player1_hider:
            hider_index = human_index
      # Get computer's move (seeker)
            seeker_row, seeker_col = self.randimazePlayer(2)
            self.last_computer_move = (seeker_row, seeker_col)
            seeker_index = seeker_row * self.N + seeker_col
        else:
            seeker_index = human_index
      # Get computer's move (hider)
            hider_row, hider_col = self.randimazePlayer(1)
            self.last_computer_move = (hider_row, hider_col)
            hider_index = hider_row * self.N + hider_col
      # Calculate game outcome
        game_result = self.game_matrix[hider_index, seeker_index]
      # Update scores based on who is hider/seeker
        if self.is_player1_hider:
            if game_result > 0:  # Hider wins
                self.player1_rounds_won += 1
                self.last_round_winner = "player1"
            else:  
      # Seeker wins
                self.player2_rounds_won += 1
                self.last_round_winner = "player2"
            self.player1_score += game_result
            self.player2_score -= game_result
        else:
            if game_result > 0:  # Hider wins
                self.player2_rounds_won += 1
                self.last_round_winner = "player2"
            else:  
      # Seeker wins
                self.player1_rounds_won += 1
                self.last_round_winner = "player1"
            self.player2_score += game_result
            self.player1_score -= game_result
        self.round += 1
        return self.last_computer_move
    def reset(self):
        self.player1_score = 0
        self.player2_score = 0
        self.player1_rounds_won = 0
        self.player2_rounds_won = 0
        self.round = 0
        self.last_human_move = None
        self.last_computer_move = None
        self.start_game()

    def simulation(self, num_rounds=100):
        self.is_player1_hider=True
        results = []
        for i in range(num_rounds):
            # Player 1 move
            if self.is_player1_hider:
                player1_row, player1_col = self.randimazePlayer(1)
                player1_index = player1_row * self.N + player1_col
                # Player 2 move
                player2_row, player2_col = self.randimazePlayer(2)
                player2_index = player2_row * self.N + player2_col
                # Determine hider and seeker indices
                hider_index = player1_index
                seeker_index = player2_index
            else :
                player1_row, player1_col = self.randimazePlayer(2)
                player1_index = player1_row * self.N + player1_col
                # Player 2 move
                player2_row, player2_col = self.randimazePlayer(1)
                player2_index = player2_row * self.N + player2_col    
            
                hider_index = player2_index
                seeker_index = player1_index
            # Calculate game outcome
            game_result = self.game_matrix[hider_index, seeker_index]
            # Determine round winner
            round_winner = None
            # Update scores based on who is hider/seeker
            if self.is_player1_hider:
                            if game_result > 0:  # Hider wins
                                self.player1_rounds_won += 1
                                round_winner = "player1"
                            else:  # Seeker wins
                                self.player2_rounds_won += 1
                                round_winner = "player2"
                            self.player1_score += game_result
                            self.player2_score -= game_result
            else:
                            if game_result > 0:  # Hider wins
                                self.player2_rounds_won += 1
                                round_winner = "player2"
                            else:  # Seeker wins
                                self.player1_rounds_won += 1
                                round_winner = "player1"
                            self.player2_score += game_result
                            self.player1_score -= game_result
                        
                
            self.round += 1
            # Store round result for visualization
            results.append({
                            'round': i + 1,
            'player1_move': (player1_row, player1_col),
                            'player2_move': (player2_row, player2_col),
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'player1_rounds_won': self.player1_rounds_won,
            'player2_rounds_won': self.player2_rounds_won,
            'round_winner': round_winner
                        })
            
            
       
        return results
    
    def tabulate_game_world(self):
        N = self.N
        
        # Create column headers (coordinates)
        headers = [""]
        for i in range(N):
                headers.append(f"{i}")
        
        # Create table rows
        table = []
        for i in range(N):
            row = [f"{i}"]
            for j in range(N):
                value = self.world[i, j]
                row.append(value)
                
            table.append(row)
        
        print(tabulate(table, headers=headers, tablefmt="grid"))

    def tabulate_game_matrix(self):
        N = self.N
        
        # Create column headers (coordinates)
        headers = ["Position"]
        for i in range(N):
            for j in range(N):
                headers.append(f"({i},{j})")
        
        # Create table rows
        table = []
        for i in range(N):
            for j in range(N):
                row_idx = i * N + j
                row = [f"({i},{j})"]  # Row label (coordinate)
                
                # Add each column value
                for k in range(N):
                    for l in range(N):
                        col_idx = k * N + l
                        value = self.game_matrix[row_idx, col_idx]
                        row.append(round(value, 2))
                
                table.append(row)
        
        print(tabulate(table, headers=headers, tablefmt="grid"))

    def tabulate_probability_vectors(self):
        N = self.N
        
        # Create table headers
        headers = ["Position", "Hider Prob (x)", "Seeker Prob (y)"]
        
        # Build table rows
        table = []
        for i in range(N):
            for j in range(N):
                idx = i * N + j
                pos_label = f"({i},{j})"
                x_prob = round(self.x_prop[idx], 6)
                y_prob = round(self.y_prop[idx], 6)
                table.append([pos_label, x_prob, y_prob])
        
        # Add game value as a footer
        result = tabulate(table, headers=headers, tablefmt="grid")
        result += f"\nGame Value: {round(self.game_value, 6)}"
        
        print(result)





def game_test():
    game = Game(N=4)
    world = [["H","H","H","N"],
             ["E","N","N","H"],
             ["N","E","N","H"],
             ["N","H","N","N"]]
    game.world = np.array(world,dtype=str)
    game.test_build()
    game.proximity()
    game.calc_probability()
    game.tabulate_game_world()
    game.tabulate_game_matrix()
    game.tabulate_probability_vectors()


game_test()    