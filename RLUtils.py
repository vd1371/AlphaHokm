import logging, sys, os, time
from feature_constructor import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint


def type_of(card):
    # for finding type of a card
    return list(card)[0]

def value_of(card):
    return int(card[1:])

def possible_actions(hand, table, hokm):
    # finding possible actions
    # returns two things: first the possible actions, second if we finished the card on the ground or not
    if len(table) == 0:
        return hand, False
    else:
        # find the ground card
        ground_card = type_of(table[0])

        # See whether we have the card or not
        possible_cards = [card for card in hand if type_of(card) == ground_card]
        if len(possible_cards) == 0:
            return hand, True
        else:
            return possible_cards, False

def card_states_on_table(table):
    ''' states on table example
    ['C2', 'C6', 'C10'], new_states = [tb1, tb2, tb3]
    ['C6', 'C10'], new_states = [tb2, tb3]
    ['C10'], new_states = [tb3]
    '''
    return [TABLE_BY_1, TABLE_BY_2, TABLE_BY_3][-len(table):] if len(table) > 0 else []

def game_status(players, table=[]):
    # for printing information
    message = "#####################################################################################\n"
    message += f'Current table {table}\n\n'
    for i, p in enumerate(players):
        message += f"Player {i} - current score: {p.mind.my_score}\n"
        message += p.get_hand() + "\n"
        message += str(p.get_knowledge()) + "\n"
    message += "#####################################################################################\n"
    return message


class Bucket:
    def __init__(self, name='Playing'):
        self.name = name
        self.x_bucket = []
        self.y_bucket = []

    def fill(self, x, y):
        for x_element, y_element in zip(x, y):
            self.x_bucket.append(x_element)
            self.y_bucket.append(y_element)

    def is_ready(self):
        return len(self.y_bucket) > 5000  # Arbitrary, it was for debugging

    def dump(self):
        df = pd.DataFrame(self.x_bucket)
        df['y'] = self.y_bucket

        states_reference = []
        for card in ALL_CARDS:
            for state in ALL_STATES:
                states_reference.append((card, state))

        #         df.columns = CARD_TYPES + states_reference + ALL_CARDS + ['R']

        df.to_csv('Bucket.csv')

    def is_ready(self):
        return len(self.y_bucket) > 50000

    def throw_away(self):
        self.x_bucket = []
        self.y_bucket = []

    def sample(self, sample_size=32):
        choices = np.random.choice(len(self.x_bucket), sample_size, replace=False)
        x_sample = np.array([self.x_bucket[x_idx] for x_idx in choices])
        y_sample = np.array([self.y_bucket[y_idx] for y_idx in choices])

        return x_sample, y_sample

    def get(self):
        return self.x_bucket, self.y_bucket


class Logger(object):
    instance = None

    def __init__(self, logger_name='Logger', address='',
                 level=logging.WARNING,
                 console_level=logging.ERROR,
                 file_level=logging.DEBUG,
                 mode='w'):
        super(Logger, self).__init__()
        if not Logger.instance:
            logging.basicConfig()

            Logger.instance = logging.getLogger(logger_name)
            Logger.instance.setLevel(level)
            Logger.instance.propagate = False

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(console_level)
            Logger.instance.addHandler(console_handler)

            file_handler = logging.FileHandler(address, mode=mode)
            file_handler.setLevel(file_level)
            formatter = logging.Formatter('%(asctime)s-%(levelname)s- %(message)s')
            file_handler.setFormatter(formatter)
            Logger.instance.addHandler(file_handler)

    def _correct_message(self, message):
        output = ''
        output += message + "\n"
        return output

    def debug(self, message):
        Logger.instance.debug(self._correct_message(message))

    def info(self, message):
        Logger.instance.info(self._correct_message(message))

    def warning(self, message):
        Logger.instance.warning(self._correct_message(message))

    def error(self, message):
        Logger.instance.error(self._correct_message(message))

    def critical(self, message):
        Logger.instance.critical(self._correct_message(message))

    def exception(self, message):
        Logger.instance.exception(self._correct_message(message))

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        print(f'---- {method.__name__} is about to start ----')
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print(f'---- {method.__name__} is done in {te - ts:.8f} seconds ----')
        return result
    return timed

if __name__ == '__main__':
    pass