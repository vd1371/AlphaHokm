# Loading dependencies
#from abc import ABC

import numpy as np
from ..Player import Player

class HokmPlayer(Player):
    round_hokm: object

    def __init__(self, **params):
        super().__init__(**params)
        '''Hokm player initialization

		Hokm player inherits from the player
			with a few more methods and attributes 
		'''

    def set_hokm(self, val):
        '''Set the hokm to players mind'''
        self.hokm = val

    def to_dict(self):
        # out_dict = {}
        # out_dict[HOKM] = self.hokm
        # out_dict[MY_SCORE] = self.my_score / (int(N_CARDS / 8) + 1)
        # out_dict[OTHER_SCORE] = self.other_score / (int(N_CARDS / 8) + 1)
        # out_dict = {**out_dict, **self.finished_cards, **self.cards_state}
        # return out_dict
        return 0

    def update_finished_cards(self, player_number, card_type, val=1):
        """
            To update the player memory of finished cards in other players hand
        """
        self.memory_finished_cards[player_number][card_type] = val

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

    def play_card(self, on_table):

        is_finished = False
        # Whether the player is lerner or not
        if len(on_table) == 0:
            selected_card = np.random.choice(self.hand)
            is_finished = True
            # The policy is that the first player selects a random card to start a round
        else:
            # This player should respect the Global Hokm and/or Round Hokm
            search_item = on_table[0].type
            for mycard in self.hand:
                if (mycard.type == search_item):
                    selected_card = mycard
                    is_finished = True
                    break
            if not is_finished:
                search_item = self.hokm
                for mycard in self.hand:
                    if (mycard.type == search_item):
                        selected_card = mycard
                        is_finished = True
                        break
                if not is_finished:
                    selected_card = np.random.choice(self.hand)

            # remove selected card from hand
        self.hand.remove(selected_card)
        # is_finished = empty_hand()
        return selected_card, not is_finished

