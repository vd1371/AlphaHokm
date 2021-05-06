# Loading dependencies
import numpy
from .Deck import Deck
from .GamesSettings import HokmSettings


class Player:
    def __init__(self, **params):
        '''Players in card games

		This class makes a payer's mind and provide
		methods for his/her actions
		name: name of player for recognition
		model: the model for deciding actions
		deck: each player must be aware of the deck he is playing
		game_settings: setting of the game that will be played
		'''
        self.name = params.pop('name')
        self.game_settings = params.pop("settings")
        self.model = params.pop('model', None)
        self.deck = params.pop('deck')
        self.STATE = params.pop('STATE', None)
        self.scores = params.pop('scores', 0)
        self.rewards = {}

        self.refresh()

    def refresh(self):
        ''' refreshing the player memory and hand

		memory_finished_cards: is the state of finished card in each players hand
			0 means no information. It is vital for the player to remember if other
			players ran out of a card type or not
		memory_cards_state: cards_state is the state of each card that can have different states
		memory = {round: {state: state, action:, reward: r}}
		'''
        self.memory_finished_cards = {}
        for i in range(1, self.game_settings.n_players):
            for card_type in self.deck.card_types:
                self.memory_finished_cards[i] = {card_type: 0}

        self.memory_cards_state = {}

        for card_type in self.deck.card_types:
            for i in range(self.deck.n_each_type_in_deck):
                self.memory_cards_state[card_type + str(i + 2)] = self.game_settings.UNKNOWN

        self.my_score = 0
        self.other_score = 0
        self.memory = {}
        self.hand = []

    def set_scores(self, scores):
        '''Set everyones score in the game

		scores could be different for different games
		'''
        self.scores = scores

    def add_cards_to_hand(self, new_hand):
        '''Adding new received cards to hand'''
        self.hand += new_hand
        self.update_cards_state(new_hand, [self.game_settings.IN_HAND for _ in range(len(new_hand))])

    def remember(self, s_a_r, round_):
        '''Remembring the state_action_reward of all rounds'''
        self.memory[round_] = s_a_r

    def play_card(self):
        '''Play a card by the player'''
        raise NotImplementedError("play is not implemented for your game")

    def get_hand(self):
        '''Get the hand length and cards in hand'''
        return f'Hand length: {len(self.hand)} Hand: {self.hand}'

    def memory_to_dict(self):
        '''This method is used to pass the player memory to learning modules'''
        raise NotImplementedError("memory_to_dict method is not implemented yet")

    def get_knowledge_str(self):
        '''This method is used to pass the player knowledge as str'''
        raise NotImplementedError("get_knowledge_str method is not implemented yet")
