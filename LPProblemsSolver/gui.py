import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np
import random
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

from Game import Game

class HideAndSeekGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hide & Seek Game")
        self.root.configure(bg="#DCC6C6")
        self.root.geometry("1200x800")
        
        # Game parameters
        self.game_size = tk.IntVar(value=4)
        self.player_name = tk.StringVar(value="Player")
        self.is_player_hider = tk.BooleanVar(value=True)
        self.is_simulation_mode = tk.BooleanVar(value=False)
        
        # Store the game instance
        self.game = None
        
        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_setup_tab()
        self.create_game_tab()
        self.create_simulation_tab()
        self.create_matrix_tab()
        self.create_vectors_tab()
        
        # Initially disable all tabs except setup
        self.disable_all_tabs_except_setup()
    
    def disable_all_tabs_except_setup(self):
        """Disable all tabs except the setup tab"""
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
    
    def enable_all_tabs(self):
        """Enable all tabs after game starts"""
        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, state="normal")
    
    def create_setup_tab(self):
        """Create the setup tab with game configuration options"""
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="Game Setup")
        
        # Title
        title_label = ttk.Label(self.setup_tab, text="Hide & Seek Game", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Create a frame for inputs
        input_frame = ttk.Frame(self.setup_tab)
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
            self.setup_tab, 
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
    
    def create_game_tab(self):
        """Create the tab for normal game play"""
        self.game_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.game_tab, text="Game Play")
        
        # Grid for game world
        self.world_frame = ttk.Frame(self.game_tab)
        self.world_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Frame for scores and stats
        self.stats_frame = ttk.Frame(self.game_tab)
        self.stats_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        
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
        
        self.last_round_result = ttk.Label(self.stats_frame, text="Last Round Result: None", font=("Arial", 12))
        self.last_round_result.pack(pady=5, anchor="w")
        
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
            command=lambda: self.notebook.select(self.matrix_tab)
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
        
    def create_simulation_tab(self):
        """Create the tab for simulation results"""
        self.simulation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_tab, text="Simulation")
        
        # Create a label for the simulation status
        self.status_label = ttk.Label(
            self.simulation_tab,
            text="Simulation not run yet",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=5)
        
        # Create a progress bar
        self.progress_bar = ttk.Progressbar(
            self.simulation_tab,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress_bar.pack(pady=5)
        
        # Create a frame with scrollbar for step-by-step results
        steps_container = ttk.Frame(self.simulation_tab)
        steps_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbar
        self.results_canvas = tk.Canvas(steps_container)
        scrollbar = ttk.Scrollbar(steps_container, orient="vertical", command=self.results_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.results_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            )
        )
        
        self.results_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.results_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create header row
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        headers = ["Round", "Hider Move", "Seeker Move", "Winner", "Player Score", "Computer Score"]
        for i, header in enumerate(headers):
            ttk.Label(header_frame, text=header, font=("Arial", 10, "bold"), width=12).grid(row=0, column=i, padx=5)
        
        # Create stats display
        self.stats_label = ttk.Label(
            self.simulation_tab,
            text="",
            font=("Arial", 12)
        )
        self.stats_label.pack(pady=10)
        
        # Add button to run simulation
        self.run_sim_button = tk.Button(
            self.simulation_tab,
            text="Run Simulation",
            font=("Arial", 12),
            bg="#FF00FF",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.run_simulation(100)
        )
        self.run_sim_button.pack(pady=10)
        
        # Add hover effect
        self.run_sim_button.bind("<Enter>", lambda e: self.run_sim_button.config(bg="#CC00CC"))
        self.run_sim_button.bind("<Leave>", lambda e: self.run_sim_button.config(bg="#FF00FF"))
    def create_matrix_tab(self):
        """Create the tab for game matrix visualization"""
        self.matrix_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.matrix_tab, text="Game Matrix")
        
        # Frame for matrix visualization
        self.matrix_frame = ttk.Frame(self.matrix_tab)
        self.matrix_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label for when no game is running
        self.matrix_placeholder = ttk.Label(
            self.matrix_frame,
            text="Start a game to view the game matrix",
            font=("Arial", 12)
        )
        self.matrix_placeholder.pack(pady=50)
    
    def create_vectors_tab(self):
        """Create the tab for strategy vectors visualization"""
        self.vectors_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.vectors_tab, text="Strategy Vectors")
        
        # Frame for X vector
        self.x_vector_frame = ttk.LabelFrame(self.vectors_tab, text="X Vector (Hider's Strategy)")
        self.x_vector_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Frame for Y vector
        self.y_vector_frame = ttk.LabelFrame(self.vectors_tab, text="Y Vector (Seeker's Strategy)")
        self.y_vector_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Placeholder labels
        ttk.Label(
            self.x_vector_frame,
            text="Start a game to view the hider's strategy vector",
            font=("Arial", 10)
        ).pack(pady=20)
        
        ttk.Label(
            self.y_vector_frame,
            text="Start a game to view the seeker's strategy vector",
            font=("Arial", 10)
        ).pack(pady=20)
    
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
        
        # Enable all tabs
        self.enable_all_tabs()
        
        # Update the role label
        self.update_role_label()
        
        # Create the world grid
        self.create_world_grid()
        
        # Switch to game tab or simulation tab based on mode
        if self.is_simulation_mode.get():
            self.notebook.select(self.simulation_tab)
        else:
            self.notebook.select(self.game_tab)
            self.notebook.tab(2, state="disabled")
        
        # Update the matrix and vectors tabs
        self.update_matrix_tab()
        self.update_vectors_tab()
    
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
        
        # Reset all cell borders
        self.create_world_grid()
        
        # Make the player's move
        computer_move = self.game.human_turn(row, col)
        
        # Highlight the human's move and computer's move with appropriate colors
        human_index = row * self.game.N + col
        comp_row, comp_col = computer_move
        comp_index = comp_row * self.game.N + comp_col
        
        # Determine the winner of the round
        if self.game.last_round_winner == "player1":
            # Player won - highlight player's move in blue, computer's in red
            self.highlight_cell(row, col, "blue", 3)
            self.highlight_cell(comp_row, comp_col, "red", 1)
            self.last_round_result.config(text="Last Round Result: You Won!")
        else:
            # Computer won - highlight player's move in red, computer's in blue  
            self.highlight_cell(row, col, "red", 1)
            self.highlight_cell(comp_row, comp_col, "blue", 3)
            self.last_round_result.config(text="Last Round Result: Computer Won!")
        
        # Update stats display
        self.update_stats()
        
        # Update the matrix and vectors tabs
        self.update_matrix_tab()
        self.update_vectors_tab()
    
    def highlight_cell(self, row, col, color, thickness):
        # Apply highlight with specified color and thickness
        self.cells[row][col].config(highlightbackground=color, highlightthickness=thickness)
    
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
            self.last_round_result.config(text="Last Round Result: None")
            
            # Update the matrix and vectors tabs
            self.update_matrix_tab()
            self.update_vectors_tab()
    
    def exit_game(self):
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit the game?"):
            self.root.destroy()
    
    def update_matrix_tab(self):
        """Update the game matrix tab with current data"""
        # Clear previous content
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        if not self.game:
            ttk.Label(self.matrix_frame, text="No game data available").pack(pady=20)
            return
        
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
        canvas = FigureCanvasTkAgg(fig, master=self.matrix_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_vectors_tab(self):
        """Update the strategy vectors tab with current data"""
        # Clear previous content
        for widget in self.x_vector_frame.winfo_children():
            widget.destroy()
        for widget in self.y_vector_frame.winfo_children():
            widget.destroy()
        
        if not self.game:
            ttk.Label(self.x_vector_frame, text="No game data available").pack(pady=20)
            ttk.Label(self.y_vector_frame, text="No game data available").pack(pady=20)
            return
        
        # Display X vector with indices
        self.create_vector_display(self.x_vector_frame, self.game.x_prop, "Hider's Strategy (X Vector)")
        
        # Display Y vector with indices
        self.create_vector_display(self.y_vector_frame, self.game.y_prop, "Seeker's Strategy (Y Vector)")

    def create_vector_display(self, parent_frame, vector, title):
        """Create a display for a strategy vector"""
        # Update the frame title
        parent_frame.config(text=title)
        
        # Create a canvas with horizontal scrollbar
        canvas = tk.Canvas(parent_frame)
        h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=canvas.xview)
        
        # Create a frame inside the canvas to hold the vector elements
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Layout for scrolling
        canvas.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Create three rows for labels (Index, Position, Probability)
        # Row 0: Headers
        ttk.Label(scrollable_frame, text="Index", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Position", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Probability", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5)
        
        # Add vector elements horizontally
        for i, prob in enumerate(vector):
            row = i // self.game.N
            col = i % self.game.N
            position = f"({row},{col})"
            
            # Place elements in columns
            column_index = i + 1  # +1 because column 0 is used for row headers
            
            ttk.Label(scrollable_frame, text=f"{i}", width=5).grid(row=0, column=column_index, padx=5, pady=2)
            ttk.Label(scrollable_frame, text=position, width=5).grid(row=1, column=column_index, padx=5, pady=2)
            ttk.Label(scrollable_frame, text=f"{prob:.6f}", width=8).grid(row=2, column=column_index, padx=5, pady=2)
    
    def run_simulation(self, num_rounds):
        self.reset_game()
        """Run the simulation and display results"""
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            if widget.grid_info()["row"] > 0:  # Keep header row
                widget.destroy()
        
        # Reset the game if needed
        if not self.game:
            self.start_game()
        
        # Disable button during simulation
        self.run_sim_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Running Simulation... Round 0/{num_rounds}")
        self.progress_bar["value"] = 0
        self.root.update()
        
        # Determine which player is hider and seeker
        player_is_hider = self.game.is_player1_hider
        
        # Run the simulation
        results = []
        for current_round in range(num_rounds):
            # Update progress
            progress = ((current_round + 1) / num_rounds) * 100
            self.progress_bar["value"] = progress
            self.status_label.config(text=f"Running Simulation... Round {current_round+1}/{num_rounds}")
            self.root.update()
            
            # Run a single round of simulation
            # Player 1 move
            player1_row, player1_col = self.game.randimazePlayer(1)
            player1_index = player1_row * self.game.N + player1_col
            
            # Player 2 move
            player2_row, player2_col = self.game.randimazePlayer(2)
            player2_index = player2_row * self.game.N + player2_col
            
            # Determine hider and seeker indices
            if player_is_hider:
                hider_index = player1_index
                seeker_index = player2_index
            else:
                hider_index = player2_index
                seeker_index = player1_index
            
            # Calculate game outcome
            game_result = self.game.game_matrix[hider_index, seeker_index]
            
            # Determine round winner
            round_winner = None
            
            # Update scores based on who is hider/seeker
            if (player_is_hider and game_result > 0) or (not player_is_hider and game_result <= 0):
                self.game.player1_rounds_won += 1
                round_winner = "player1"
            else:
                self.game.player2_rounds_won += 1
                round_winner = "player2"
                
            self.game.player1_score += game_result if player_is_hider else -game_result
            self.game.player2_score -= game_result if player_is_hider else -game_result
            
            self.game.round += 1
            
            # Create a result dictionary
            result = {
                'round': current_round + 1,
                'player1_move': (player1_row, player1_col),
                'player2_move': (player2_row, player2_col),
                'player1_score': self.game.player1_score,
                'player2_score': self.game.player2_score,
                'player1_rounds_won': self.game.player1_rounds_won,
                'player2_rounds_won': self.game.player2_rounds_won,
                'round_winner': round_winner
            }
            
            results.append(result)
            
            # Add this result to the display
            self.add_result_to_display(result, current_round + 1, player_is_hider)
            
            # Update stats
            self.update_stats_display()
        
        # Simulation complete
        self.progress_bar["value"] = 100
        self.status_label.config(text="Simulation Complete!")
        self.run_sim_button.config(state=tk.NORMAL)
        
        # Display summary
        summary = f"Final Results:\n" \
                f"{self.game.player1_name} Score: {self.game.player1_score}\n" \
                f"{self.game.player2_name} Score: {self.game.player2_score}\n\n" \
                f"{self.game.player1_name} Rounds Won: {self.game.player1_rounds_won}\n" \
                f"{self.game.player2_name} Rounds Won: {self.game.player2_rounds_won}"
        
        self.stats_label.config(text=summary)
        
        # Update the matrix and vectors tabs
        self.update_matrix_tab()
        self.update_vectors_tab()
    
    def add_result_to_display(self, result, row_num, player_is_hider):
        # Create a frame for this result
        round_frame = ttk.Frame(self.scrollable_frame)
        round_frame.grid(row=row_num, column=0, sticky="ew", pady=2)
        
        # Round number
        ttk.Label(round_frame, text=str(result['round']), width=12).grid(row=0, column=0, padx=5)
        
        # Hider move
        if player_is_hider:
            hider_move = result['player1_move']
        else:
            hider_move = result['player2_move']
        ttk.Label(round_frame, text=f"({hider_move[0]},{hider_move[1]})", width=12).grid(row=0, column=1, padx=5)
        
        # Seeker move
        if player_is_hider:
            seeker_move = result['player2_move']
        else:
            seeker_move = result['player1_move']
        ttk.Label(round_frame, text=f"({seeker_move[0]},{seeker_move[1]})", width=12).grid(row=0, column=2, padx=5)
        
        # Winner
        winner_text = self.game.player1_name if result['round_winner'] == "player1" else self.game.player2_name
        ttk.Label(round_frame, text=winner_text, width=12).grid(row=0, column=3, padx=5)
        
        # Player score
        ttk.Label(round_frame, text=str(result['player1_score']), width=12).grid(row=0, column=4, padx=5)
        
        # Computer score
        ttk.Label(round_frame, text=str(result['player2_score']), width=12).grid(row=0, column=5, padx=5)
        
        # Autoscroll to show the latest entry
        self.results_canvas.yview_moveto(1.0)

    def update_stats_display(self):
        # Update the stats display during simulation
        stats_text = f"Current Status:\n" \
                    f"{self.game.player1_name} Score: {self.game.player1_score}\n" \
                    f"{self.game.player2_name} Score: {self.game.player2_score}\n\n" \
                    f"{self.game.player1_name} Rounds Won: {self.game.player1_rounds_won}\n" \
                    f"{self.game.player2_name} Rounds Won: {self.game.player2_rounds_won}"
        
        self.stats_label.config(text=stats_text)



if __name__ == "__main__":
    root = tk.Tk()
    app = HideAndSeekGUI(root)
    root.mainloop()        