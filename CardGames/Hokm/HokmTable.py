# Loading dependencies
import numpy as np
from ..Deck import Deck
from ..GamesSettings import HokmSettings
from .HokmPlayer import HokmPlayer
from CardGames.utils import Logger


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
        self.logger.info(f'Hakem is global player {self.hakem}. {initial_hand} is the first hand')

        # Select hokm out of the five variable
        self.hokm = self.players[self.hakem].select_hokm()
        self._update_hokm_knowledge(self.hokm)  # new knowledge
        self.logger.info(f'{self.hokm} is chosen as hokm')

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
        # self.logger.info(f'{tmp_cards} are added to player {next_player} hand')
        return

    def _analyze_round(self, table_cards):
        '''Who won this round?
        The player with the highest value wins the round
        If anyone plays any hokm card, the highest hokm card wins the round
        input: dict of  # key: card, value( i = the i th played card, turn = by global player number)
        '''
        first = True
        for card in table_cards:
            # For the first player
            if first:
                first_card_type = card.type
                highest_card = card
                first = False

            elif card.type == self.hokm:  # This act is called "Cutting"
                if self.hokm != highest_card.type:  # Boridan for the first time
                    highest_card = card
                elif (card.number) > (highest_card.number):  # Boridan va Sar kardan
                    highest_card = card
            # Comply with the table
            elif ((highest_card.type == card.type) and (card.number > highest_card.number)):
                highest_card = card

        # Finding winner's index
        winner = table_cards[highest_card][1]
        other_winner = (winner + 2) % self.settings.n_players

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
        self.logger.info(f'player.rewards: {rewards}')
        return winner, rewards

    def _select_cards(self, n):
        # for initialization
        selected = np.random.choice(self.unallocated_cards, n, replace=False)
        self.unallocated_cards = list(set(self.unallocated_cards) - set(selected))
        return list(selected)

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

            self.logger.info(f'{player.name} knowledge: {player.memory_cards_state}')

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

            action, is_finished = self.players[turn].play_card(table, mcts_model=HokmMCTS)
            # when a player runs out of a card
            if is_finished:
                self._update_finished_card_knowledge(turn, table[0].type)
            # getting the action of the player
            round_s_a_r[turn][i] = action
            # logging the action
            self.logger.info(f'Player {turn} action is: {action} is_finish: {is_finished}')
            # self.logger.info(f'It is {self.turn} turn to start the round {n_round}')

            # updating the table
            table.append(action)
            played_cards[action] = (
                i, turn)  # key: card, value( i = the i th played card, turn = by global player number)

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

        # self.logger.info(f'The winner is global player {round_winner}. The played cards were {played_cards}')
        # self.logger.debug(f'\nPlayers knowledge at round {n_round}, episode {self.episode}:\n' + game_status(self.players, table))

        self.logger.info(f'------------------------------------------------')
        self.logger.info(f'Table: {table}')
        self.logger.info(f'------------------------------------------------')

    def game_over(self):
        '''
        This is a hyperparameter, we should check whether playing to the last card or plating till one wins
        would change the performance of the model
        My initial guess: Play till the last card
        '''
        if self.players[0].scores == HokmSettings.SCORE_TO_WIN or \
                self.players[1].scores == HokmSettings.SCORE_TO_WIN:
            return True
        elif len(self.players[0].hand) > 0:
            return False
        else:
            return True

    def mcts_play_one_round(self, on_table, idx, n_round=1):
        # initialize meta state action rewards dict
        round_s_a_r = {}
        for i in range(self.settings.n_players):
            round_s_a_r[i] = {}
        table = []
        # add the on_table cards on the table
        for card in on_table:
            table.append(card)

        played_cards = {}  # key: player, value: card
        # played_cards = {}  # key: player, value: card
        i = self.hakem
        for card in table:
            played_cards[card] = (i, i % self.settings.n_players)
            i = i + 1
        # key: card, value( i = the i th played card, turn = by global player number)

        # self.logger.info(f'Episode:{self.episode}. It is {self.turn} turn to start the round {n_round}')
        for i in range(self.settings.n_players - len(table)):
            turn = (self.turn + i) % self.settings.n_players
            self.logger.info(f'Table: {table}')
            self.logger.info(self.players[turn].get_hand())
            # update the player's knowledge based on the cards on the table
            if i > 0:
                self.players[turn].update_cards_state(table, card_states_on_table(table))
            # getting the state of the player before playing the game
            round_s_a_r[turn]['state'] = self.players[turn].memory_to_dict()

            if (self.turn == turn):
                action = self.players[turn].hand[idx]
                is_finished = False
            else:
                action, is_finished = self.players[turn].play_card(table, mcts_model=HokmMCTS)

            # when a player runs out of a card
            if is_finished:
                self._update_finished_card_knowledge(turn, table[0].type)
            # getting the action of the player
            round_s_a_r[turn][i] = action
            # logging the action
            # self.logger.info(f'Player {turn} action is: {action} is_finish: {is_finished}')
            # self.logger.info(f'It is {self.turn} turn to start the round {n_round}')

            # updating the table
            table.append(action)
            played_cards[action] = (
                i, turn)  # key: card, value( i = the i th played card, turn = by global player number)

            self.logger.info(f'------------------------------------------------')

        # updating the knowledge of player of played cards
        self._update_played_card_knowledge(played_cards)

        round_winner, rewards = self._analyze_round(played_cards)

        for i in range(self.settings.n_players):
            # reward[i][1] this is True of False, whether he has won or not
            self.players[i].update_score(rewards[i][1])
            round_s_a_r[i]['reward'] = rewards[i][0]

        self._update_players_memory(round_s_a_r, n_round)
        return (self.turn == round_winner)


def card_states_on_table(table):
    """
    states on table example
    ['C2', 'C6', 'C10'], new_states = [tb1, tb2, tb3]
    ['C6', 'C10'], new_states = [tb2, tb3]
    ['C10'], new_states = [tb3]
    """
    return [HokmSettings.TABLE_BY_1, HokmSettings.TABLE_BY_2, HokmSettings.TABLE_BY_3][-len(table):] if len(
        table) > 0 else []


def HokmMCTS(memory, hand, on_table, possible_cards, n_mcts_sims=10):
    # n_mcts_sims -> the number of play to decide but select card randomly
    ''' Monte Carlo Tree Search for Hokm

    ##TODO: Complete this code
    '''
    logger = Logger()
    probabilities = np.zeros(len(possible_cards))

    print(memory)
    # input()

    for j in range(n_mcts_sims):

        # Create a deck
        deck = Deck()

        to_be_removed = []
        tblcnt = 0
        for card in deck.all_cards:

            if memory[card.type + str(card.number)] != 'unk':
                to_be_removed.append(card)
            if memory[card.type + str(card.number)].find("tb") >= 0:
                tblcnt = tblcnt + 1;

            # update the turn
            turn = tblcnt % 4;

        # only keep the unknown cards from the memroy in the deck and remove the rest of them
        deck.remove_cards(to_be_removed)
        # randomly select a card from possible_cards
        selected_card = np.random.choice(possible_cards)
        idx = possible_cards.index(selected_card)

        # instantiate the players with the deck and make them all play randomly (strategy = "random")
        p0 = HokmPlayer(name='AlexRandom', deck=deck, settings=HokmSettings, strategy='random')
        p1 = HokmPlayer(name='RyanRandom', deck=deck, settings=HokmSettings, strategy='random')
        p2 = HokmPlayer(name='JimmyRandom', deck=deck, settings=HokmSettings, strategy='random')
        p3 = HokmPlayer(name='MathewRandom', deck=deck, settings=HokmSettings, strategy='random')

        # set the hokm from memory to the new table
        hokm = memory['hokm']

        # instantiate a new hokm table
        hokm_table = HokmTable(p0, p1, p2, p3,
                               deck=deck,
                               hokm=hokm,
                               turn=turn,
                               settings=HokmSettings,
                               logger=logger)
        hokm_table.mcts_initialize(hand)

        # then similar to what happend in run.py

        # while not hokm_table.game_over():
        # play rounds
        if hokm_table.mcts_play_one_round(on_table, idx, n_round=1):
            probabilities[idx] += 1

    # find the card with highest probability of winning and return it
    return possible_cards[np.argmax(probabilities)]

    # update anything else you think is necessary, like players' scores

    # play that specific round the player is about to decide

    # if the player is winner, then add 1 to the probabilities
    # probabilities[idx] += 1

    # return np.random.choice(possible_cards)

