# Loading dependencies
#from abc import ABC

import numpy as np
from ..Player import Player
from .HokmMCTS import HokmMCTS

class HokmPlayer(Player):
	round_hokm: object

	def __init__(self, **params):
		super().__init__(**params)
		'''Hokm player initialization

		Hokm player inherits from the player with a few more methods and attributes 
		'''
		self.strategy = params.pop("strategy", 'random')

	def set_hokm(self, val):
		'''Set the hokm to players mind'''
		self.hokm = val

	def to_dict(self):
		out_dict = {}
		out_dict['hokm'] = self.hokm
		out_dict['my_score'] = self.my_score / (int(self.deck.n_cards / 8) + 1)
		out_dict['other_score'] = self.other_score / (int(self.deck.n_cards / 8) + 1)
		out_dict = {**out_dict, **self.memory_finished_cards, **self.memory_cards_state}
		return out_dict

	def update_score(self, winner = True):
		if winner:
			self.add_my_score()
		self.set_other_score(len(self.hand))

	def add_my_score(self, score = 1):
		self.my_score += score

	def set_other_score(self, n_remaining_cards):
		self.other_score = int(self.deck.n_cards / 4) - n_remaining_cards - self.my_score

	def update_finished_cards_state(self, player_number, card_type):
		'''To update the player memory of finished cards in other players hand'''
		self.memory_finished_cards[card_type + "_of_" + str(player_number)] = 1

	def update_cards_state(self, cards, new_states):
		'''To update the player memory of cards state'''
		for card, state in zip (cards, new_states):
			self.memory_cards_state[card] = state

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

		possible_cards, is_finished = possible_actions(self.hand, on_table, self.hokm)

		if self.strategy == 'random':
			selected_card = np.random.choice(possible_cards)

		elif self.strategy == 'MCTS':
			selected_card = HokmMCTS(self.memory, self.hand, possible_cards)

		elif self.strategy == 'DQN':
			raise NotImplementedError ("DQN is not implemented yet")

		else:
			raise ValueError ("player.strategy MUST be random, MCTS, or DQN, but it's not"
								"Check for typo")

		##TODO: please update the possible_actions to be compatible with your algorithm
		##BUG: in your code, when there is no card on the table, is_finished is True
		##but is_finished is a message that will be used if and only if the plays "cut"
		##please consider this in the code
		## if it's finished, please clean the code and remove unnecessary lines

		# is_finished = False
		# # Whether the player is lerner or not
		# if len(on_table) == 0:
		#     selected_card = np.random.choice(self.hand)
		#     is_finished = True
		#     # The policy is that the first player selects a random card to start a round
		# else:
		#     # This player should respect the Global Hokm and/or Round Hokm
		#     search_item = on_table[0].type
		#     for mycard in self.hand:
		#         if (mycard.type == search_item):
		#             selected_card = mycard
		#             is_finished = True
		#             break
		#     if not is_finished:
		#         search_item = self.hokm
		#         for mycard in self.hand:
		#             if (mycard.type == search_item):
		#                 selected_card = mycard
		#                 is_finished = True
		#                 break
		#         if not is_finished:
		#             selected_card = np.random.choice(self.hand)


		# remove selected card from hand
		self.hand.remove(selected_card)
		return selected_card, is_finished


def possible_actions(hand, table, hokm):
	# finding possible actions
	# returns two things: first the possible actions, second if we finished the card on the ground or not
	if len(table) == 0:
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