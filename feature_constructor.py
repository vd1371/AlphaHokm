import numpy as np

## p_ft : playing feature transformation
## h_ft : hokming feature transformation

# Game settings
N_CARDS = 52
N_FOR_HOKM = 5
N_PLAYERS = 4
SCORE_TO_WIN = int(N_CARDS/8)+1

# General Variables
HOKM = 'hokm'
MY_SCORE, OTHER_SCORE = 'my_score', 'other_score'
STATE, ACTION, REWARD = 'S', 'A', 'R'

# Game Variables
CARD_TYPES = ('C', 'S', 'H', 'D') # Khaj: Club, Pik: Spades, Del: Hearts, Khesht: Diamonds
UNKNOWN, IN_HAND = 'unk', 'inh' 
PLAYED_BY_0, PLAYED_BY_1, PLAYED_BY_2, PLAYED_BY_3  = 'by0', 'by1', 'by2', 'by3'
TABLE_BY_1, TABLE_BY_2, TABLE_BY_3 = 'tb1', 'tb2', 'tb3'
ALL_STATES = [PLAYED_BY_0, PLAYED_BY_1, PLAYED_BY_2, PLAYED_BY_3, TABLE_BY_1, TABLE_BY_2, TABLE_BY_3, IN_HAND]
ALL_CARDS = ()
for c_type in CARD_TYPES:
        for i in range(int(N_CARDS/4)):
            ALL_CARDS += (c_type + str(i+2),)

#####Info: scroes    hokm states    finished cards states           other cards_state             
DIMENSION =  2 + len(CARD_TYPES) + N_PLAYERS*len(CARD_TYPES)-4 + (1+len(ALL_STATES))*(N_CARDS)

class playerMind:
    def __init__(self):
        self.name = 'Playing Feature Constructor'
        self.hokm = None
        # cards_state is the state of each card that can have 9 different states
        self.cards_state = {}
        for c_type in CARD_TYPES:
            for i in range(int(N_CARDS/4)):
                self.cards_state[c_type + str(i+2)] = UNKNOWN
        # finished_cards_state is the state of finished card in each players hand
        self.finished_cards = {}
        for i in range(1, N_PLAYERS):
            for c_type in CARD_TYPES:
                self.finished_cards[c_type + "_of_" + str(i)] = 0
            
        self.my_score = 0
        self.other_score = 0
        
        # This is for feature transformation
        self.cards_state_tuples = []
        for card in ALL_CARDS:
            for state in ALL_STATES:
                self.cards_state_tuples.append((card, state))
        
    def set_hokm(self, val):
        self.hokm = val
    def update_cards_state(self, cards, new_states):
        for card, state in zip (cards, new_states):
            self.cards_state[card] = state
    def update_finished_cards_state(self, player_number, card_type):
        self.finished_cards[card_type + "_of_" + str(player_number)] = 1
        
    def add_my_score(self):
        self.my_score += 1
    def set_other_score(self, n_remaining_cards):
        self.other_score = int(N_CARDS/4) - n_remaining_cards - self.my_score
        
    def to_dict(self):
        out_dict = {}
        out_dict[HOKM] = self.hokm
        out_dict[MY_SCORE] = self.my_score/(int(N_CARDS/8)+1)
        out_dict[OTHER_SCORE] = self.other_score/(int(N_CARDS/8)+1)
        out_dict = {**out_dict, **self.finished_cards, **self.cards_state}
        return out_dict
    
    def forget(self):
        self.__init__()
        
        