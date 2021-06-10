from ..RLUtils import *

class PlayingFeatureTransformer:
    def __init__(self):
        self.states_actions = ALL_CARDS[:]
        self.states_reference = []
        for card in ALL_CARDS:
            for state in ALL_STATES:
                self.states_reference.append((card, state))

    def transform(self, knowledge, played_card):

        scores = [knowledge[MY_SCORE], knowledge[OTHER_SCORE]]

        h = np.zeros(len(CARD_TYPES))  # state of hokm
        f = [knowledge[k] for k in knowledge if '_of_' in k]
        s = np.zeros(len(self.states_reference))  # state of cards themselves
        a = np.zeros(N_CARDS)  # action encoded

        h[CARD_TYPES.index(knowledge[HOKM])] = 1

        for card, state in knowledge.items():
            if len(card) <= 3 and state != UNKNOWN:
                idx = self.states_reference.index((card, state))
                s[idx] = 1
        a[ALL_CARDS.index(played_card)] = 1

        return np.concatenate((scores, h, f, s, a))

    def init_for_playing_card(self, knowledge):
        self._scores = [knowledge[MY_SCORE], knowledge[OTHER_SCORE]]

        self._h = np.zeros(len(CARD_TYPES))
        self._s = np.zeros(len(self.states_reference))
        self._f = [knowledge[k] for k in knowledge if '_of_' in k]
        for card, state in knowledge.items():
            if len(card) <= 3 and state != UNKNOWN:
                idx = self.states_reference.index((card, state))
                self._s[idx] = 1

    def transform_when_playing(self, played_card):
        a = np.zeros(N_CARDS)
        a[ALL_CARDS.index(played_card)] = 1
        return np.concatenate((self._scores, self._f, self._h, self._s, a))



class HokmingFeatureTransformer:
    def __init__(self):
        pass

    def transform(self, initial_hand, hokm):
        s = np.zeros(N_CARDS)
        a = np.zeros(len(CARD_TYPES))

        for card in initial_hand:
            s[ALL_CARDS.index(card)] = 1
        a[CARD_TYPES.index(hokm)] = 1

        return np.concatenate((s, a))

if __name__ == "__main__":
    fs = PlayingFeatureTransformer()
    fs.transform(['C2'], 'C')