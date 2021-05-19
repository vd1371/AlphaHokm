# Loading dependencies
# from abc import ABC

import numpy as np
from ..Player import Player


class HokmPlayer(Player):
    round_hokm: object

    def __init__(self, **params):
        super().__init__(**params)
        '''Hokm player initialization
        Hokm player inherits from the player with a few more methods and attributes 
        '''
        self.strategy = params.pop("strategy", 'random')
        self.logger = params.pop("logger", None)


    def set_hokm(self, val):
        '''Set the hokm to players mind'''
        self.hokm = val

    def memory_to_dict(self):
        out_dict = {}
        out_dict['hokm'] = self.hokm
        out_dict['my_score'] = self.my_score / (int(self.deck.n_cards / 8) + 1)
        out_dict['other_score'] = self.other_score / (int(self.deck.n_cards / 8) + 1)
        out_dict = {**out_dict, **self.memory_finished_cards, **self.memory_cards_state}
        return out_dict

    def update_score(self, winner=True):
        if winner:
            self.add_my_score()
        self.set_other_score(len(self.hand))

    def add_my_score(self, score=1):
        self.my_score += score

    def set_other_score(self, n_remaining_cards):
        self.other_score = int(self.deck.n_cards / 4) - n_remaining_cards - self.my_score

    def remember_hakem(self, hakem):
        self.memory_of_hakem = hakem

    def update_finished_cards_state(self, player_number, card_type):
        '''To update the player memory of finished cards in other players hand'''
        self.memory_finished_cards[card_type + "_of_" + str(player_number)] = 1

    def update_cards_state(self, cards, new_states):
        '''To update the player memory of cards state'''
        for card, state in zip(cards, new_states):
            # self.memory_cards_state[card] = state   ### Ava
            self.memory_cards_state[card.__str__()] = state

    def select_hokm(self):
        """
        Selecting Hokm by the player
        Selecting hokm in Hokm has almost a fixed rule
        The card type with the highest sum of values in hand
        """
        tmp_dict = {}
        possible_hokms = list(set([card.type for card in self.hand]))

        vals = np.zeros(len(possible_hokms))
        for card in self.hand:
            idx = possible_hokms.index(card.type)
            vals[idx] += card.number

        return possible_hokms[np.argmax(vals)]

    def empty_hand(self):
        return len(self.hand) == 0

    def play_card(self, table, played_cards = None, mcts_model = None):

        possible_cards, is_finished = possible_actions(self.hand, table, self.hokm)
        #self.logger.info(f'{self.name}: possible_cards: {possible_cards}');
        # print(f'possible_cards: {possible_cards}');

        if self.strategy == 'random':
            selected_card = np.random.choice(possible_cards)

        elif self.strategy == 'MCTS':
            # print ("HERE1---->", len(self.hand))
            selected_card = mcts_model(self.memory_to_dict(),
                                        self.hand,
                                        table,
                                        played_cards,
                                        possible_cards)

        elif self.strategy == 'DQN':
            raise NotImplementedError("DQN is not implemented yet")

        else:
            raise ValueError("player.strategy MUST be random, MCTS, or DQN, but it's not"
                             "Check for typo")
        # remove selected card from hand
        self.hand.remove(selected_card)
        return selected_card, is_finished

def possible_actions(hand, table, hokm):
    # finding possible actions
    # returns two things: first the possible actions, second if we finished the card on the ground or not

    possible_cards: list = []
    if len(table) == 0:
        # Table is empty and all cards in hand is possible to play
        return hand, False
    else:
        # find the ground card
        ground_card = table[0].type

        # See whether we have the card or not
        possible_cards = [card for card in hand if card.type == ground_card]
        if len(possible_cards) == 0:
            return hand, True
        else:
            return possible_cards, False