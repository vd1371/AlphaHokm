# Loading dependencies
import numpy as np


class Card:
    def __init__(self, card_type, number):
        self.type = card_type
        self.number = number

    def __str__(self):
        return self.type + str(self.number)

    def __repr__(self):
        return self.type + str(self.number)

    def __hash__(self):
        return hash((self.type, self.number))

    def __eq__(self, other):
        if self.type == other.type and self.number == other.number:
            return True
        return False

class Deck:
    def __init__(self, **params):
        """
        Constructor params:
		n_cards: total number of cards in the deck
		n_players: number of players playing the game
		card_types: card types in the deck
		D: Diamond, C: Club, S: Spades, H: Hearts
		"""
        self.n_cards = params.pop("n_cards", 52)
        self.card_types = params.pop("card_types", ('D', 'C', 'S', 'H'))

        # Finding number of card types
        self.n_card_types = len(self.card_types)
        # Finding the number of cards with a specific type in a deck
        assert self.n_cards % self.n_card_types == 0, "Remainder of " \
                                                      "n_cards / n_card_types must be Zero"

        self.n_each_type_in_deck = int(self.n_cards / self.n_card_types)

        # Creating the deck
        self.all_cards = []
        for card_type in self.card_types:
            for j in range(self.n_each_type_in_deck):
                # '+2' is used because cards start from 2, like D2
                self.all_cards.append(Card(card_type, j + 2))

        # Shuffle the deck
        self.shuffle()

    def shuffle(self):
        """Shuffle all cards"""
        np.random.shuffle(self.all_cards)

    def draw_cards(self, n):
        """Drawing n cards from a shuffle deck"""
        selected_cards = self.all_cards[:n]
        self.all_cards = self.all_cards[n:]
        return selected_cards

    def empty(self):
        return len(self.all_cards) == 0

    def remove_card(self, to_be_removed):
        '''To remove a card from the deck'''
        self.all_cards.remove(to_be_removed)

    def remove_cards(self, to_be_removed):
        """ This method gets parameters as a list, tuple, or dictionary
		and removes those cards from the deck
		This method can be used in MCTS

		##TODO: complete this method accordingly
		"""
        for card in to_be_removed:
            self.all_cards.remove(card)
