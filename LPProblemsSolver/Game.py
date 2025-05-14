import numpy as np
import random
class Game:
    def __init__(self, round_num = 0, player1_name="player1", player2_name="player2", N=4, is_player1_hider=True):
        self.round = round_num
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.N = N
        self.is_player1_hider = is_player1_hider
        self.player1_prop = []
        self.player2_prop = []
        self.game_matrix = np.zeros((N**2,N**2))
        self.world = np.full((N,N),"",dtype=str)
    def reset():
        pass
    def randimazePlayer(self,player:int):
        pass
    def simulation():
        pass
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
                                        
    def calc_probability(self):
        pass
    def start_game(self):
        #set N
        self.build()
        self.proximity()
        self.calc_probability()
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
game.build_test()        