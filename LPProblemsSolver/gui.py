import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np
import random
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

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
        self.player1_prop = [0]*self.num_of_places
        self.player2_prop = [0]*self.num_of_places
        self.tmp_player1_prop = [0]*self.num_of_places
        self.tmp_player2_prop = [0]*self.num_of_places
        self.smallest_element1 = 0
        self.smallest_element2 = 0
        self.game_value = 0
        
        # For tracking the last moves
        self.last_human_move = None
        self.last_computer_move = None
        self.last_round_winner = None
    
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
                                        
    def build_constraint(self, type: str):
        # Set up the coefficient matrix for constraints
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
            c=x_input['c'],
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
            self.player1_prop = x_result.x[:self.num_of_places]
            self.player2_prop = y_result.x[:self.num_of_places]
            
            non_zero_indices = [i for i, x in enumerate(self.player1_prop) if x != 0]
            self.smallest_element1 = min(self.player1_prop[i] for i in non_zero_indices) if non_zero_indices else 0
            
            non_zero_indices = [i for i, x in enumerate(self.player2_prop) if x != 0]
            self.smallest_element2 = min(self.player2_prop[i] for i in non_zero_indices) if non_zero_indices else 0
            
            # The optimal value of the game is the negative of the objective value
            self.game_value = -x_result.fun
            
            self.tmp_player1_prop = self.player1_prop.copy()
            self.tmp_player2_prop = self.player2_prop.copy()
            
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
            hider_row, hider_col = self.randimazePlayer(2)
            self.last_computer_move = (hider_row, hider_col)
            hider_index = hider_row * self.N + hider_col
        
        # Calculate game outcome
        game_result = self.game_matrix[hider_index, seeker_index]
        hider_score = self.game_matrix[hider_index, seeker_index]
        
        # Update scores based on who is hider/seeker
        if self.is_player1_hider:
            if game_result > 0:  # Hider wins
                self.player1_rounds_won += 1
            else:  # Seeker wins
                self.player2_rounds_won += 1
            self.player1_score += hider_score
            self.player2_score -= game_result
        else:
            if game_result > 0:  # Hider wins
                self.player2_rounds_won += 1
            else:  # Seeker wins
                self.player1_rounds_won += 1
            self.player2_score += hider_score
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
        results = []
        for i in range(num_rounds):
            # Player 1 move
            player1_row, player1_col = self.randimazePlayer(1)
            player1_index = player1_row * self.N + player1_col
            
            # Player 2 move
            player2_row, player2_col = self.randimazePlayer(2)
            player2_index = player2_row * self.N + player2_col
            
            # Determine hider and seeker indices
            if self.is_player1_hider:
                hider_index = player1_index
                seeker_index = player2_index
            else:
                hider_index = player2_index
                seeker_index = player1_index
            
            # Calculate game outcome
            game_result = self.game_matrix[hider_index, seeker_index]
            hider_score = self.game_matrix[hider_index, seeker_index]
            
            # Update scores based on who is hider/seeker
            if self.is_player1_hider:
                if game_result > 0:  # Hider wins
                    self.player1_rounds_won += 1
                else:  # Seeker wins
                    self.player2_rounds_won += 1
                self.player1_score += hider_score
                self.player2_score -= game_result
            else:
                if game_result > 0:  # Hider wins
                    self.player2_rounds_won += 1
                else:  # Seeker wins
                    self.player1_rounds_won += 1
                self.player2_score += hider_score
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
                'player2_rounds_won': self.player2_rounds_won
            })
        
        return results


class HideAndSeekGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hide & Seek Game")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("1200x800")
        
        # Game parameters
        self.game_size = tk.IntVar(value=4)
        self.player_name = tk.StringVar(value="Player")
        self.is_player_hider = tk.BooleanVar(value=True)
        self.is_simulation_mode = tk.BooleanVar(value=False)
        
        # Store the game instance
        self.game = None
        
        # Create the setup frame
        self.create_setup_frame()
        
        # Create the game frame (initially hidden)
        self.create_game_frame()
        
        # Create the strategy frame (initially hidden)
        self.create_strategy_frame()
        
        # Hide game frames initially
        self.game_frame.pack_forget()
        self.strategy_frame.pack_forget()
    
    def create_setup_frame(self):
        self.setup_frame = ttk.Frame(self.root, padding="20")
        self.setup_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.setup_frame, text="Hide & Seek Game", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Create a frame for inputs
        input_frame = ttk.Frame(self.setup_frame)
        input_frame.pack(pady=10)
        
        # World size input
        size_frame = ttk.Frame(input_frame)
        size_frame.pack(pady=10, fill=tk.X)
        
        size_label = ttk.Label(size_frame, text="World Size (N):", font=("Arial", 12))
        size_label.pack(side=tk.LEFT, padx=10)
        
        size_options = [2, 3, 4, 5, 6]
        size_dropdown = ttk.Combobox(size_frame, textvariable=self.game_size, values=size_options, width=5)
        size_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Player name input
        name_frame = ttk.Frame(input_frame)
        name_frame.pack(pady=10, fill=tk.X)
        
        name_label = ttk.Label(name_frame, text="Player Name:", font=("Arial", 12))
        name_label.pack(side=tk.LEFT, padx=10)
        
        name_entry = ttk.Entry(name_frame, textvariable=self.player_name, width=20)
        name_entry.pack(side=tk.LEFT, padx=10)
        
        # Player role selection
        role_frame = ttk.Frame(input_frame)
        role_frame.pack(pady=10, fill=tk.X)
        
        role_label = ttk.Label(role_frame, text="Player Role:", font=("Arial", 12))
        role_label.pack(side=tk.LEFT, padx=10)
        
        hider_radio = ttk.Radiobutton(role_frame, text="Hider", variable=self.is_player_hider, value=True)
        hider_radio.pack(side=tk.LEFT, padx=10)
        
        seeker_radio = ttk.Radiobutton(role_frame, text="Seeker", variable=self.is_player_hider, value=False)
        seeker_radio.pack(side=tk.LEFT, padx=10)
        
        # Game mode selection
        mode_frame = ttk.Frame(input_frame)
        mode_frame.pack(pady=10, fill=tk.X)
        
        mode_label = ttk.Label(mode_frame, text="Game Mode:", font=("Arial", 12))
        mode_label.pack(side=tk.LEFT, padx=10)
        
        normal_radio = ttk.Radiobutton(mode_frame, text="Normal Game", variable=self.is_simulation_mode, value=False)
        normal_radio.pack(side=tk.LEFT, padx=10)
        
        simulation_radio = ttk.Radiobutton(mode_frame, text="Simulation Mode (100 rounds)", variable=self.is_simulation_mode, value=True)
        simulation_radio.pack(side=tk.LEFT, padx=10)
        
        # Start button
        start_button = tk.Button(
            self.setup_frame, 
            text="Start Game", 
            font=("Arial", 14, "bold"),
            bg="#FF00FF",  # Fuchsia
            fg="white",
            padx=20,
            pady=10,
            command=self.start_game
        )
        start_button.pack(pady=20)
        
        # Add hover effect to start button
        start_button.bind("<Enter>", lambda e: start_button.config(bg="#CC00CC"))
        start_button.bind("<Leave>", lambda e: start_button.config(bg="#FF00FF"))
    
    def create_game_frame(self):
        self.game_frame = ttk.Frame(self.root, padding="10")
        
        # Grid for game world
        self.world_frame = ttk.Frame(self.game_frame)
        self.world_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        # Frame for scores and stats
        self.stats_frame = ttk.Frame(self.game_frame)
        self.stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        
        # Labels for stats
        self.round_label = ttk.Label(self.stats_frame, text="Round: 0", font=("Arial", 12))
        self.round_label.pack(pady=5, anchor="w")
        
        self.player1_score_label = ttk.Label(self.stats_frame, text="Player Score: 0", font=("Arial", 12))
        self.player1_score_label.pack(pady=5, anchor="w")
        
        self.player2_score_label = ttk.Label(self.stats_frame, text="Computer Score: 0", font=("Arial", 12))
        self.player2_score_label.pack(pady=5, anchor="w")
        
        self.player1_wins_label = ttk.Label(self.stats_frame, text="Player Rounds Won: 0", font=("Arial", 12))
        self.player1_wins_label.pack(pady=5, anchor="w")
        
        self.player2_wins_label = ttk.Label(self.stats_frame, text="Computer Rounds Won: 0", font=("Arial", 12))
        self.player2_wins_label.pack(pady=5, anchor="w")
        
        self.role_label = ttk.Label(self.stats_frame, text="Role: ", font=("Arial", 12))
        self.role_label.pack(pady=5, anchor="w")
        
        self.last_move_label = ttk.Label(self.stats_frame, text="Last Computer Move: None", font=("Arial", 12))
        self.last_move_label.pack(pady=5, anchor="w")
        
        # Buttons
        buttons_frame = ttk.Frame(self.stats_frame)
        buttons_frame.pack(pady=20)
        
        self.reset_button = tk.Button(
            buttons_frame, 
            text="Reset Game", 
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.view_strategy_button = tk.Button(
            buttons_frame, 
            text="View Strategy", 
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=self.toggle_strategy_view
        )
        self.view_strategy_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = tk.Button(
            buttons_frame, 
            text="Exit Game", 
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=self.exit_game
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # Add hover effects to buttons
        for button in [self.reset_button, self.view_strategy_button, self.exit_button]:
            button.bind("<Enter>", lambda e, b=button: b.config(bg="#CC00CC"))
            button.bind("<Leave>", lambda e, b=button: b.config(bg="#FF00FF"))
    
    def create_strategy_frame(self):
        self.strategy_frame = ttk.Frame(self.root, padding="10")
        
        # Frame for matrix visualization
        self.matrix_frame = ttk.Frame(self.strategy_frame)
        self.matrix_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Close button for strategy view
        self.close_strategy_button = tk.Button(
            self.strategy_frame, 
            text="Close Strategy View", 
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=self.toggle_strategy_view
        )
        self.close_strategy_button.pack(pady=10)
        
        # Add hover effect
        self.close_strategy_button.bind("<Enter>", lambda e: self.close_strategy_button.config(bg="#CC00CC"))
        self.close_strategy_button.bind("<Leave>", lambda e: self.close_strategy_button.config(bg="#FF00FF"))
    
    def start_game(self):
        # Get game parameters
        N = self.game_size.get()
        player_name = self.player_name.get()
        is_player_hider = self.is_player_hider.get()
        
        # Create the game
        self.game = Game(
            player1_name=player_name,
            player2_name="Computer",
            N=N,
            is_player1_hider=is_player_hider
        )
        
        # Initialize the game
        if not self.game.start_game():
            messagebox.showerror("Error", "Failed to initialize game. Please try again.")
            return
        
        # Hide setup frame and show game frame
        self.setup_frame.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update the role label
        self.update_role_label()
        
        # Create the world grid
        self.create_world_grid()
        
        # If simulation mode, run simulation
        if self.is_simulation_mode.get():
            self.run_simulation()
    
    def create_world_grid(self):
        # Clear previous grid
        for widget in self.world_frame.winfo_children():
            widget.destroy()
        
        # Create cell size based on the window size
        cell_size = min(400 // self.game.N, 80)
        
        # Create a header row and column for coordinates
        # Header row (column indices)
        tk.Label(self.world_frame, text="", width=2).grid(row=0, column=0)
        for j in range(self.game.N):
            tk.Label(self.world_frame, text=str(j), font=("Arial", 10, "bold"), width=2).grid(row=0, column=j+1)
        
        # Create cells
        self.cells = []
        for i in range(self.game.N):
            # Row header (row indices)
            tk.Label(self.world_frame, text=str(i), font=("Arial", 10, "bold"), width=2).grid(row=i+1, column=0)
            
            row_cells = []
            for j in range(self.game.N):
                difficulty = self.game.world[i, j]
                
                # Choose background color based on difficulty
                if difficulty == "E":
                    bg_color = "#AAFFAA"  # Light green for Easy
                    difficulty_text = "E (Easy)"
                elif difficulty == "N":
                    bg_color = "#FFFFAA"  # Light yellow for Neutral
                    difficulty_text = "N (Neutral)"
                else:  # "H"
                    bg_color = "#FFAAAA"  # Light red for Hard
                    difficulty_text = "H (Hard)"
                
                cell = tk.Button(
                    self.world_frame,
                    text=f"({i},{j})\n{difficulty_text}",
                    width=8,
                    height=3,
                    bg=bg_color,
                    command=lambda row=i, col=j: self.cell_click(row, col)
                )
                cell.grid(row=i+1, column=j+1, padx=2, pady=2)
                row_cells.append(cell)
            
            self.cells.append(row_cells)
    
    def cell_click(self, row, col):
        if self.is_simulation_mode.get():
            messagebox.showinfo("Simulation Mode", "Cannot make moves in simulation mode.")
            return
        
        # Make the player's move
        computer_move = self.game.human_turn(row, col)
        
        # Highlight the human's move
        self.highlight_cell(row, col, "blue")
        
        # Highlight the computer's move
        if computer_move:
            comp_row, comp_col = computer_move
            self.highlight_cell(comp_row, comp_col, "red")
        
        # Update stats display
        self.update_stats()
    
    def highlight_cell(self, row, col, color):
        # Store the original background color
        original_bg = self.cells[row][col].cget("bg")
        
        # Highlight with a border
        self.cells[row][col].config(highlightbackground=color, highlightthickness=3)
        
        # Schedule to remove the highlight after a delay
        self.root.after(2000, lambda: self.remove_highlight(row, col, original_bg))
    
    def remove_highlight(self, row, col, original_bg):
        if hasattr(self, 'cells') and row < len(self.cells) and col < len(self.cells[row]):
            self.cells[row][col].config(highlightthickness=0)
    
    def update_stats(self):
        # Update the stats labels
        self.round_label.config(text=f"Round: {self.game.round}")
        self.player1_score_label.config(text=f"{self.game.player1_name} Score: {self.game.player1_score}")
        self.player2_score_label.config(text=f"{self.game.player2_name} Score: {self.game.player2_score}")
        self.player1_wins_label.config(text=f"{self.game.player1_name} Rounds Won: {self.game.player1_rounds_won}")
        self.player2_wins_label.config(text=f"{self.game.player2_name} Rounds Won: {self.game.player2_rounds_won}")
        
        # Update last move label
        if self.game.last_computer_move:
            self.last_move_label.config(text=f"Last Computer Move: {self.game.last_computer_move}")
    
    def update_role_label(self):
        if self.game.is_player1_hider:
            role_text = f"{self.game.player1_name} (Hider) vs {self.game.player2_name} (Seeker)"
        else:
            role_text = f"{self.game.player1_name} (Seeker) vs {self.game.player2_name} (Hider)"
        self.role_label.config(text=f"Role: {role_text}")
    
    def reset_game(self):
        if self.game:
            self.game.reset()
            self.create_world_grid()
            self.update_stats()
    
    def exit_game(self):
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit the game?"):
            self.root.destroy()
    
    def toggle_strategy_view(self):
        if self.strategy_frame.winfo_manager():
            self.strategy_frame.pack_forget()
            self.game_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.game_frame.pack_forget()
            self.strategy_frame.pack(fill=tk.BOTH, expand=True)
            self.visualize_strategy()
    
    def visualize_strategy(self):
        # Clear previous visualizations
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        # Create tabs for different visualizations
        notebook = ttk.Notebook(self.matrix_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tab for game matrix
        game_matrix_tab = ttk.Frame(notebook)
        notebook.add(game_matrix_tab, text="Game Matrix")
        
        # Create tab for probabilities
        probabilities_tab = ttk.Frame(notebook)
        notebook.add(probabilities_tab, text="Strategy Probabilities")
        
        # Visualize the game matrix
        self.visualize_game_matrix(game_matrix_tab)
        
        # Visualize the probabilities
        self.visualize_probabilities(probabilities_tab)
    
    def visualize_game_matrix(self, tab):
        # Create a figure for the game matrix
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create a heatmap of the game matrix
        im = ax.imshow(self.game.game_matrix, cmap='RdYlGn')
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Payoff", rotation=-90, va="bottom")
        
        # Add labels and title
        ax.set_title("Game Matrix (Hider's Payoff)")
        
        # Add row and column labels
        ax.set_xlabel("Seeker's Strategies")
        ax.set_ylabel("Hider's Strategies")
        
        # Add grid coordinates as labels
        row_labels = [f"({i//self.game.N},{i%self.game.N})" for i in range(self.game.num_of_places)]
        col_labels = [f"({i//self.game.N},{i%self.game.N})" for i in range(self.game.num_of_places)]
        
        # Set tick positions and labels
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(col_labels)
        ax.set_yticklabels(row_labels)
        
        # Rotate the column labels and set their alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Loop over data dimensions and create text annotations
        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                text = ax.text(j, i, self.game.game_matrix[i, j],
                              ha="center", va="center", color="black")
        
        # Adjust layout
        fig.tight_layout()
        
        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def visualize_probabilities(self, tab):
        # Create figure for probabilities
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Prepare data for hider's probabilities
        hider_probs = self.game.player1_prop if self.game.is_player1_hider else self.game.player2_prop
        hider_labels = [f"({i//self.game.N},{i%self.game.N})" for i in range(self.game.num_of_places)]
        
        # Prepare data for seeker's probabilities
        seeker_probs = self.game.player2_prop if self.game.is_player1_hider else self.game.player1_prop
        seeker_labels = [f"({i//self.game.N},{i%self.game.N})" for i in range(self.game.num_of_places)]
        
        # Plot hider's probabilities
        ax1.bar(hider_labels, hider_probs, color='green')
        ax1.set_title("Hider's Strategy Probabilities")
        ax1.set_xlabel("Position (row,col)")
        ax1.set_ylabel("Probability")
        
        # Rotate labels for better readability
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Plot seeker's probabilities
        ax2.bar(seeker_labels, seeker_probs, color='red')
        ax2.set_title("Seeker's Strategy Probabilities")
        ax2.set_xlabel("Position (row,col)")
        ax2.set_ylabel("Probability")
        
        # Rotate labels for better readability
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Adjust layout
        fig.tight_layout()
        
        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def run_simulation(self):
        # Disable buttons during simulation
        self.reset_button.config(state=tk.DISABLED)
        self.view_strategy_button.config(state=tk.DISABLED)
        
        # Run the simulation
        results = self.game.simulation(num_rounds=100)
        
        # Update stats
        self.update_stats()
        
        # Enable buttons
        self.reset_button.config(state=tk.NORMAL)
        self.view_strategy_button.config(state=tk.NORMAL)
        
        # Show summary
        summary = f"Simulation Results:\n\n" \
                 f"{self.game.player1_name} Score: {self.game.player1_score}\n" \
                 f"{self.game.player2_name} Score: {self.game.player2_score}\n\n" \
                 f"{self.game.player1_name} Rounds Won: {self.game.player1_rounds_won}\n" \
                 f"{self.game.player2_name} Rounds Won: {self.game.player2_rounds_won}"
        
        messagebox.showinfo("Simulation Complete", summary)
        
        # Create a detailed results window
        self.show_simulation_results(results)
    
    def show_simulation_results(self, results):
        # Create a new window for detailed results
        results_window = tk.Toplevel(self.root)
        results_window.title("Simulation Detailed Results")
        results_window.geometry("800x600")
        
        # Create a figure for the score progression
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Extract data for plotting
        rounds = [r['round'] for r in results]
        player1_scores = [r['player1_score'] for r in results]
        player2_scores = [r['player2_score'] for r in results]
        player1_wins = [r['player1_rounds_won'] for r in results]
        player2_wins = [r['player2_rounds_won'] for r in results]
        
        # Plot score progression
        ax1.plot(rounds, player1_scores, 'b-', label=f"{self.game.player1_name} Score")
        ax1.plot(rounds, player2_scores, 'r-', label=f"{self.game.player2_name} Score")
        ax1.set_title("Score Progression")
        ax1.set_xlabel("Round")
        ax1.set_ylabel("Score")
        ax1.legend()
        ax1.grid(True)
        
        # Plot rounds won progression
        ax2.plot(rounds, player1_wins, 'b-', label=f"{self.game.player1_name} Rounds Won")
        ax2.plot(rounds, player2_wins, 'r-', label=f"{self.game.player2_name} Rounds Won")
        ax2.set_title("Rounds Won Progression")
        ax2.set_xlabel("Round")
        ax2.set_ylabel("Rounds Won")
        ax2.legend()
        ax2.grid(True)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create a canvas to display the figure
        canvas = FigureCanvasTkAgg(fig, master=results_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add a close button
        close_button = tk.Button(
            results_window,
            text="Close",
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=results_window.destroy
        )
        close_button.pack(pady=10)
        
        # Add hover effect
        close_button.bind("<Enter>", lambda e: close_button.config(bg="#CC00CC"))
        close_button.bind("<Leave>", lambda e: close_button.config(bg="#FF00FF"))


if __name__ == "__main__":
    root = tk.Tk()
    app = HideAndSeekGUI(root)
    root.mainloop()