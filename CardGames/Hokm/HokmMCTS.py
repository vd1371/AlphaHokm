#Loading dependencies
import numpy as np
import time
from copy import deepcopy

from ..GamesSettings import HokmSettings
from ..Deck import Deck

from .HokmPlayer import HokmPlayer
from .HokmUtils import analyze_round

class HokmTableForMCTS:
	
	def __init__(self, *players, **params):
		"""
		HokmTable constructor
		players: list of 4 players playing this game
		deck: a deck of card
		hakem: the idx of the person who is going to choose hokm
		"""
		self.players = players
		self.deck = params.pop('deck')
		self.hakem = params.pop('hakem', 0)
		self.hokm = params.pop('hokm', 'H')
		self.turn = params.pop('turn', 0)
		self.settings = params.pop('settings')

	def _update_hokm_knowledge(self, val):
		for p in self.players:
			p.set_hokm(val)

	def _analyze_round(self, played_cards):

		winner, other_winner = analyze_round(played_cards, self.hokm, self.settings.n_players)
		rewards = {}
		for i in range(self.settings.n_players):
			if i == winner or i == other_winner:
				rewards[i] = (-1, True)
			else:
				rewards[i] = (-1, False)
		# self.logger.info(f'player.rewards: {rewards}')
		return winner, rewards

	def mcts_initialize(self, hand):
		self.players[self.turn].add_cards_to_hand(hand)
		self._update_hokm_knowledge(self.hokm)  # new knowledge

		# Finding next player index
		next_player = (self.turn + 1) % self.settings.n_players
		while not next_player == self.turn:
			if (next_player < self.turn):
				tmp_cards = self.deck.draw_cards(len(hand) - 1)
			else:
				tmp_cards = self.deck.draw_cards(len(hand))
			self.players[next_player].add_cards_to_hand(tmp_cards)
			next_player = (next_player + 1) % self.settings.n_players

	def mcts_play_one_round(self, table=None, action=None, played_cards = None, n_round = 1):
		# add the on_table cards on the table
		if table is None:
			table = []

		played_cards = {}  # key: player, value: card
		i = self.hakem

		if len(table) > 0:
			for card in table:
				played_cards[card] = (i, i % self.settings.n_players)
				i = i + 1

		n_iter = self.settings.n_players if len(table) > 0 else self.settings.n_players - len(table)
		
		for i in range(n_iter):
			turn = (self.turn + i) % self.settings.n_players

			if self.turn == turn and not action is None:
				self.players[turn].hand.remove(action)
			
			else:
				action, _ = self.players[turn].play_card(table)

			# updating the table
			table.append(action)

			# key: card, value( i = the i th played card, turn = by global player number)
			played_cards[action] = (i, turn)

		round_winner, rewards = self._analyze_round(played_cards)
		# updating the knowledge of player of played cards
		for i in range(self.settings.n_players):
			# reward[i][1] this is True of False, whether he has won or not
			self.players[i].update_score(rewards[i][1])

		self.turn = round_winner
		return (round_winner, rewards)

	def game_over(self):
		'''
		This is a hyperparameter, we should check whether playing to the last card or plating till one wins
		would change the performance of the model
		My initial guess: Play till the last card
		'''
		if self.players[0].my_score == HokmSettings.SCORE_TO_WIN or \
				self.players[1].my_score == HokmSettings.SCORE_TO_WIN:
			return True
		elif len(self.players[0].hand) > 0:
			return False
		else:
			return True



def HokmMCTS(memory, hand, table, played_cards, possible_cards):
	# n_mcts_sims -> the number of play to decide but select card randomly
	''' Monte Carlo Tree Search for Hokm'''

	start = time.time()
	probabilities = np.zeros(len(possible_cards))

	# This is derived for finding the number of mcts
	n_round = int(13 - memory['my_score'] - memory['other_score'])
	n_mcts_sims = (n_round - 1) * 10

	# If there is only one option, just return that card
	if len(possible_cards) == 1:
		return possible_cards[0]

	else:
		# Create a deck
		deck = Deck()
		to_be_removed = []
		tblcnt = 0
		for card in deck.all_cards:
			if memory[card.__str__()] != 'unk':
				to_be_removed.append(card)

		# update the turn
		org_turn = len(table)

		# only keep the unknown cards from the memroy in the deck and remove the rest of them
		deck.remove_cards(to_be_removed)

		for j in range(n_mcts_sims):

			n_round = int(memory['my_score'] + memory['other_score'])
			# instantiate the players with the deck and make them all play randomly (strategy = "random")
			p0 = HokmPlayer(name='AlexRandom', deck=deck, settings=HokmSettings, strategy='random')
			p1 = HokmPlayer(name='RyanRandom', deck=deck, settings=HokmSettings, strategy='random')
			p2 = HokmPlayer(name='JimmyRandom', deck=deck, settings=HokmSettings, strategy='random')
			p3 = HokmPlayer(name='MathewRandom', deck=deck, settings=HokmSettings, strategy='random')

			# randomly select a card from possible_cards
			selected_card = np.random.choice(possible_cards)
			idx = possible_cards.index(selected_card)

			temp_table = deepcopy(table)
			temp_deck = deepcopy(deck)
			temp_hand = deepcopy(hand)

			# instantiate a new hokm table
			hokm_table = HokmTableForMCTS(p0, p1, p2, p3,
								   deck=temp_deck,
								   hokm=memory['hokm'],
								   turn=org_turn,
								   settings=HokmSettings)

			hokm_table.mcts_initialize(temp_hand)

			# play rounds
			temp_round_winner, temp_rewards = hokm_table.mcts_play_one_round(temp_table,
																			 selected_card,
																			 played_cards,
																			 n_round)
			while not hokm_table.game_over():
				n_round += 1
				temp_round_winner = hokm_table.mcts_play_one_round(n_round = n_round)

			p0_sum = hokm_table.players[0].my_score
			p1_sum = hokm_table.players[1].my_score

			tt = org_turn
			if (org_turn > 1):
				tt = (org_turn + 2) % 4


			if (p0_sum > p1_sum) and (tt == 0):
				probabilities[idx] += 1
			if (p0_sum < p1_sum) and (tt == 1):
				probabilities[idx] += 1

		# find the card with highest probability of winning and return it
		print (f"MCTS : {time.time()-start:.2f} <<<<<<<<<<<<<<<<<<<")
		return possible_cards[np.argmax(probabilities)]