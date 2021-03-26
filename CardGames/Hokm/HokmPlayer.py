#Loading dependencies
import numpy as np
from ..Player import Player

class HokmPlayer(Player):
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

	def update_finished_cards(self, player_number, card_type, val = 1):
		'''To update the player memory of finished cards in other players hand'''
		self.memory_finished_cards[player_number][card_type] = val

	def select_hokm(self):
		'''Selecting Hokm by the player
		
		Selecting hokm in Hokm has almost a fixed rule
		The card type with the highest sum of values in hand
		'''
		tmp_dict = {}
		possible_hokms = list(set([card.type for card in self.hand]))

		vals = np.zeros(len(possible_hokms))
		for card in self.hand:
			idx = possible_hokms.index(card.type)
			vals[idx] += card.number

		return possible_hokms[np.argmax(vals)]

	def empty_hand(self):
		return len(self.hand) == 0

	def play_card(self, on_table, eps0=0.5, eps1=0.5):
		# Whether the player is lerner or not
		eps = eps0 if self.fast_learner else eps1
		
		# Finding the cards that could be played , and whether the player has ran out of that card or not
		lawful_cards, is_finished = possible_actions(self.hand, on_table, self.mind.hokm)
		
		# Predicting the q_value of ALL card given the current state
		probabilities = self.model.predict_policy(self.p_transform(self.mind.to_dict()))
		
		lawful_cards_probs = []
		for i, card in enumerate(lawful_cards):
			# Adding the value of the cards in lawful cards
			lawful_cards_probs.append(probabilities[card_number(card)])
		
		# selecting the card with highest q_value
		if self.fast_learner:
			try:
				lawful_cards_probs = lawful_cards_probs/np.sum(lawful_cards_probs)
				selected_card = np.random.choice(lawful_cards, p=lawful_cards_probs)
			except:
				selected_card = np.random.choice(lawful_cards)
		else:
			selected_card = np.random.choice(lawful_cards)
			
		# remove selected card from hand
		self.hand.remove(selected_card) 
		return selected_card, is_finished

	def get_memory(self):
		# TODO: Complete this part
		mem = "\n"
		for round in self.memory.keys():
			mem += f'Round {round}\n'
			state = self.memory[round][STATE]
#             mem += f'State:     Hokm:{state[HOKM]}\n'
			mem += f"State:     Hokm:{state[HOKM]}, self score:{state[MY_SCORE]}, other score:{state[OTHER_SCORE]}\n"
			for card_type in CARD_TYPES:
				for key, val in state.items():
					if card_type in key:
						mem += f'{key}:{val}, '
				mem += '\n'
			mem += f'Action {self.memory[round][ACTION]}. Reward {self.memory[round][REWARD]}\n\n'
		return mem