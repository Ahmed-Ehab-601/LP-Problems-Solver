from sympy import Matrix, pprint
class Game:
    def __init__(self, round_num, player1_name, player2_name, N, is_player1_hider):
        self.round = round_num
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0
        self.N = N
        self.is_player1_hider = is_player1_hider
        self.player1_prop = []
        self.player2_prop = []
        self.game_matrix =Matrix.zeros(N**2,N**2)
        self.world=Matrix.zeros(N,N)
    def reset():
        pass
    def randimazePlayer(self,player:int):
        pass
    def simulation():
        pass
    def proximity(self):
        pass
    def build(self):
        pass
    def calc_probability(self):
        pass
    def start_game(self):
        pass
    def human_turn(self):     
        pass

    

    