#Loading dependencies
import numpy as np

class HokmTable:
    def __init__(self, *players, **params):
        '''HokmTable constructor

        players: list of 4 players playing this game
        deck: a deck of card
        hakem: the idx of the person who is going to choose hokm
        '''
        self.players = players
        self.deck = params.pop('deck')
        self.hakem = params.pop('hakem')
        self.settings = params.pop('settings')
        self.logger = params.pop('logger', None)
    
    def settings(self, reward =100, loss =0, step_r = 0, step_l = 0):
        '''Rewards and losses for this game to be used in RL'''
        self.reward = reward
        self.loss= loss
        self.step_reward = step_r
        self.step_loss = step_l

    def initialize(self):
        self.turn = self.hakem

        # Select five cards and give it to hakem, then choose hokm
        initial_hand = self.deck.draw_cards(self.settings.n_for_hokm)
        self.players[self.hakem].add_cards_to_hand(initial_hand)
#         logger.info(f'Hakem is global player {self.hakem}. {initial_hand} are chosen to choose hokm')
        
        # Select hokm out of the five variable
        self.hokm = self.players[self.hakem].select_hokm()
        self._update_hokm_knowledge(self.hokm)  ### new knowledge
#         logger.info(f'{self.hokm} is chosen as hokm')
        
        # Finding next player index
        next_player = (self.turn + 1) % self.settings.n_players
        # Now draw cards for other players
        while not self.deck.empty():
        
            if self.players[next_player].empty_hand():
                tmp_cards = self.deck.draw_cards(self.settings.n_for_hokm)
            else:
                tmp_cards = self.deck.draw_cards(self.settings.n_each_hand - self.settings.n_for_hokm)
            self.players[next_player].add_cards_to_hand(tmp_cards)
            next_player = (next_player + 1) % self.settings.n_players
#             logger.info(f'{tmp_cards} are added to player {next_player} hand')

        return initial_hand, self.hokm

    def _analyze_step(self, table_cards):
        '''Who won this step?

        The player with the highest value wins the step
        If anyone plays any hokm card, the highest hokm card wins the step
        input: dict of  # key: card, value( i = the i th played card, turn = by global player number) 
        '''
        first = True
        for card in table_cards:
            # For the first player
            if first:
                first_card_type = card.type_
                highest_card = card
                first = False

            if card.type_ == self.hokm: # This act is called "Cutting"
                if self.hokm != highest_card.type_: # BOridan for the first time 
                    highest_card = card
                elif value_of(card) > value_of(highest_card): # Boridan va Sar kardan
                    highest_card = card
            elif card.type_ == ground_card and value_of(card) > value_of(highest_card): # Comply with the table
                highest_card = card

        # Finding winner's index
        winner = table_cards[highest_card][1]
        other_winner = (winner+2) % N_PLAYERS
        
        if self.players[winner].mind.my_score == int(N_CARDS/8):
            r = self.reward
            l = self.loss
        else:
            r = self.regular_reward
            l = self.regular_loss
        
        rewards = {}
        for i in range(N_PLAYERS):
            if i == winner or i == other_winner:
                rewards[i] = (r, True)
            else:
                rewards[i]= (l, False)
                
        return winner, rewards
    
    def _select_cards(self, n):
        # for initialization
        selected = np.random.choice(self.unallocated_cards, n, replace=False)
        self.unallocated_cards = list(set(self.unallocated_cards)-set(selected))
        return list(selected)
    
    def _update_hokm_knowledge(self, val):
        for p in self.players:
            p.set_hokm(val)
    
    def _update_players_memory(self, round_s_a_r, n_round):
        for i, player in enumerate(self.players):
            player.remember(round_s_a_r[i], n_round)
    
    def _update_played_card_knowledge(self, played_cards):
        bys = [PLAYED_BY_0, PLAYED_BY_1, PLAYED_BY_2, PLAYED_BY_3]
        new_set = list(played_cards.keys())
        for i, player in enumerate(self.players):
            '''
            e.g. played_card = {'C2': (0, 2), 'H3': (1, 3), 'C4': (2, 0), 'S2': (3, 1)} self.turn = 2
            for player_0: 'C2':by2, 'H3':by3, 'C4':by0, 'S2':by1
            for player_1: 'C2':by1, 'H3':by2, 'C4':by3, 'S2':by0
            for player_2: 'C2':by0, 'H3':by1, 'C4':by2, 'S2':by3
            for player_3: 'C2':by3, 'H3':by0, 'C4':by1, 'S2':by3
            '''
            pointer = (self.turn - i) % N_PLAYERS
            new_states = bys[pointer:] + bys[:pointer]
            player.mind.update_cards_state(new_set, new_states)
    
    def _update_finished_card_knowledge(self, player_number, card_type):
        '''
        e.g. player #1 has finished the H
        for player_0: H_of_1 : True
        for player_1: H_of_0 : True
        for player_2: H_of_3 : True
        for player_3: H_of_2 : True
        '''
        for i, p in enumerate(self.players):
            local_number = (player_number - i) % N_PLAYERS
            if not local_number == 0:
                p.mind.update_finished_cards_state(local_number, card_type)
    
    def reset(self, episode, previous_winner):
        for p in self.players:
            p.reset()
        self.episode = episode
        # previous_winner is either 0 or 1, current turn could be 0, 1, 2, 3
        if (previous_winner + self.hakem) % 2 == 1:
            # if the opponent team wins, the hakem will change, otherwise, it remains the same
            self.hakem = (self.hakem + 1) % N_PLAYERS
            
        
    
        
    def play_one_round(self, n_round = 1):
        # initialize meta state action rewards dict
        round_s_a_r = {}
        for i in range(N_PLAYERS):
            round_s_a_r[i] = {}
        table = []
        played_cards = {} # key: player, value: card

#         logger.info(f'Episode:{self.episode}. It is {self.turn} turn to start the round {n_round}') 
        for i in range (N_PLAYERS):
            turn = (self.turn + i) % N_PLAYERS
            
#             logger.info(f'Table: {table}')
#             logger.info(self.players[turn].get_hand())
            if i > 0 :
                self.players[turn].mind.update_cards_state(table, card_states_on_table(table)) # update the player's knowledge based on the cards on the table
            
            round_s_a_r[turn][STATE] = self.players[turn].mind.to_dict()  # getting the state of the player before playing the game
#             logger.info(f'\nPlayer {turn} knowledge:\n' + self.players[turn].get_knowledge()) # logging the player knowledge before playing the game
            
            action, is_finished = self.players[turn].play_card(table)
            if is_finished: # when a player runs out of a card
                self._update_finished_card_knowledge(turn, type_of(table[0]))
                
            round_s_a_r[turn][ACTION] = action # getting the action of the player
#             logger.info(f'Player {turn} action is: ' + action) # logging the action
#             logger.info(f'------------------------------------------------')
            
            table.append(action) # updating the table
            played_cards[action] = (i, turn) # key: card, value( i = the i th played card, turn = by global player number) 
        
        # updating the knowledge of player of played cards
        self._update_played_card_knowledge(played_cards)
        round_winner, reward = self._analyze_round(played_cards)
        for i in range(N_PLAYERS):
            self.players[i].update_score(reward[i][1])  #reward[i][1] this is True of False, whether he has won or not 
            round_s_a_r[i][REWARD] = reward[i][0]
        
        self._update_players_memory(round_s_a_r, n_round)
        self.turn = round_winner
        
#         logger.info(f'The winner is global player {round_winner}. The played cards were {played_cards}')
#         logger.debug(f'\nPlayers knowledge at round {n_round}, episode {self.episode}:\n' + game_status(self.players, table))
    
    def game_over(self):
        '''
        This is a hyperparameter, we should check whether playing to the last card or plating till one wins
        would change the performance of the model
        My initial guess: Play till the last card
        '''
        return self.players[0].mind.my_score== SCORE_TO_WIN or self.players[1].mind.my_score == SCORE_TO_WIN
        return False if len(self.players[0].hand) > 0 else True
        
if __name__ == "__main__":
    
    p0 = HokmPlayer('Alex', fast_learner = True, eps = eps)
    p1 = HokmPlayer('Ryan', fast_learner = False, eps = eps)
    p2 = HokmPlayer('Jimmy', fast_learner = True, eps = eps)
    p3 = HokmPlayer('Mathew', fast_learner = False, eps = eps)
    
    myHokmTable = HokmTable(p0, p1, p2, p3)
    myHokmTable.initialize(0.5, 0.5)
    for _ in range(7):
        n_round = 0
        while not myHokmTable.game_over():
            n_round += 1
            myHokmTable.play_one_round(n_round = n_round)
            p0_sum = table.players[0].score
            p1_sum = table.players[1].score
            print (p0_sum, p1_sum)
            winner = 0 if p0_sum >= p1_sum else 1
    