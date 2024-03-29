# Loading dependencies
import numpy as np
import time

from ..Deck import Deck
from ..GamesSettings import HokmSettings
from ..utils import Logger

from .HokmMCTS import HokmMCTS
from .HokmUtils import analyze_round

class HokmTable:
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
		self.logger = params.pop('logger', None)

		self.rl_settings()

	def rl_settings(self, reward=100, loss=0, round_r=10, round_l=0):
		"""Rewards and losses for this game to be used in RL"""
		self.reward = reward
		self.loss = loss
		self.round_reward = round_r
		self.round_loss = round_l

	def initialize(self):
		self.turn = self.hakem

		# Select five cards and give it to hakem, then choose hokm
		initial_hand = self.deck.draw_cards(self.settings.n_for_hokm)
		self.players[self.hakem].add_cards_to_hand(initial_hand)
		# self.logger.info(f'Hakem is global player {self.hakem}. {initial_hand} is the first hand')

		# Select hokm out of the five variable
		self.hokm = self.players[self.hakem].select_hokm()
		self._update_hokm_knowledge(self.hokm)  # new knowledge
		self.logger.info(f'{self.hokm} is chosen as hokm by {self.turn}')

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
		# self.logger.info(f'{tmp_cards} are added to player {next_player} hand')

		return initial_hand, self.hokm

	def _analyze_round(self, played_cards):

		winner, other_winner = analyze_round(played_cards, self.hokm, self.settings.n_players)

		if self.players[winner].my_score == int(self.players[winner].deck.n_cards / 8):
			r = self.reward
			l = self.loss
		else:
			r = self.round_reward
			l = self.round_loss

		rewards = {}
		for i in range(self.settings.n_players):
			if i == winner or i == other_winner:
				rewards[i] = (r, True)
			else:
				rewards[i] = (l, False)
		# self.logger.info(f'player.rewards: {rewards}')
		return winner, rewards

	def _update_hokm_knowledge(self, val):
		for p in self.players:
			p.set_hokm(val)

	def _update_players_memory(self, round_s_a_r, n_round):
		for i, player in enumerate(self.players):
			player.remember(round_s_a_r[i], n_round)

	def _update_played_card_knowledge(self, played_cards):
		bys = [HokmSettings.PLAYED_BY_0, HokmSettings.PLAYED_BY_1,
			   HokmSettings.PLAYED_BY_2, HokmSettings.PLAYED_BY_3]
		new_set = list(played_cards.keys())
		for i, player in enumerate(self.players):
			'''
			e.g. played_card = {'C2': (0, 2), 'H3': (1, 3), 'C4': (2, 0), 'S2': (3, 1)} self.turn = 2
			for player_0: 'C2':by2, 'H3':by3, 'C4':by0, 'S2':by1
			for player_1: 'C2':by1, 'H3':by2, 'C4':by3, 'S2':by0
			for player_2: 'C2':by0, 'H3':by1, 'C4':by2, 'S2':by3
			for player_3: 'C2':by3, 'H3':by0, 'C4':by1, 'S2':by3
			'''
			pointer = (self.turn - i) % self.settings.n_players
			new_states = bys[pointer:] + bys[:pointer]
			player.update_cards_state(new_set, new_states)

			# self.logger.info(f'{player.name} knowledge: {player.memory_cards_state}')

	def _update_finished_card_knowledge(self, player_number, card_type):
		'''
		e.g. player #1 has finished the H
		for player_0: H_of_1 : True
		for player_1: H_of_0 : True
		for player_2: H_of_3 : True
		for player_3: H_of_2 : True
		'''
		for i, player in enumerate(self.players):
			local_number = (player_number - i) % self.settings.n_players
			if not local_number == 0:
				player.update_finished_cards_state(local_number, card_type)

	# def reset(self, episode, previous_winner):
	def reset(self, previous_winner):
		for p in self.players:
			p.reset()
		# self.episode = episode
		# previous_winner is either 0 or 1, current turn could be 0, 1, 2, 3
		if (previous_winner + self.hakem) % 2 == 1:
			# if the opponent team wins, the hakem will change, otherwise, it remains the same
			self.hakem = (self.hakem + 1) % self.settings.n_players

	def play_one_round(self, n_round=1):
		# initialize meta state action rewards dict
		round_s_a_r = {}
		for i in range(self.settings.n_players):
			round_s_a_r[i] = {}

		table = []
		played_cards = {}  # key: player, value: card


		self.logger.info(f'It is {self.turn} turn to start the round {n_round}')

		# self.logger.info(f'Episode:{self.episode}. It is {self.turn} turn to start the round {n_round}')
		for i in range(self.settings.n_players):
			turn = (self.turn + i) % self.settings.n_players

			self.logger.info(f'Table: {table}')
			self.logger.info(self.players[turn].get_hand())

			# update the player's knowledge based on the cards on the table
			if i > 0:
				self.players[turn].update_cards_state(table, card_states_on_table(table))
			# getting the state of the player before playing the game
			round_s_a_r[turn]['state'] = self.players[turn].memory_to_dict()

			action, is_finished = self.players[turn].play_card(table,
																played_cards = played_cards,
																mcts_model=HokmMCTS)
			
			# when a player runs out of a card
			if is_finished:
				self._update_finished_card_knowledge(turn, table[0].type)
			# getting the action of the player
			round_s_a_r[turn][i] = action
			
			# logging the action
			self.logger.info(f'Player {turn} action is: {action} is_finish: {is_finished}')


			# updating the table
			table.append(action)

			# key: card, value( i = the i th played card, turn = by global player number)
			played_cards[action] = (i, turn)

			self.logger.info(f'------------------------------------------------')

		# updating the knowledge of player of played cards
		self._update_played_card_knowledge(played_cards)

		round_winner, rewards = self._analyze_round(played_cards)
		for i in range(self.settings.n_players):
			# reward[i][1] this is True of False, whether he has won or not
			self.players[i].update_score(rewards[i][1])

			round_s_a_r[i]['reward'] = rewards[i][0]

		self._update_players_memory(round_s_a_r, n_round)
		
		self.turn = round_winner
		self.logger.info(f'The winner is global player {round_winner}. The played cards were {played_cards}')
		# self.logger.debug(f'\nPlayers knowledge at round {n_round}, episode {self.episode}:\n' + game_status(self.players, table))
		self.logger.info(f'------------------------------------------------')
		self.logger.info(f'Table: {table}')
		self.logger.info(f'------------------------------------------------')
		return round_winner

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


def card_states_on_table(table):
	"""
	states on table example
	['C2', 'C6', 'C10'], new_states = [tb1, tb2, tb3]
	['C6', 'C10'], new_states = [tb2, tb3]
	['C10'], new_states = [tb3]
	"""
	return [HokmSettings.TABLE_BY_1, HokmSettings.TABLE_BY_2, HokmSettings.TABLE_BY_3][-len(table):] if len(
		table) > 0 else []



