'''Settings of all current and future games

Thid module consists of several other modules
each of which describing the corresponding game
settings
'''
class HokmSettings:
    n_players=4
    # States for feature transformation and logging
    UNKNOWN = 'unk'
    IN_HAND = 'inh'
    PLAYED_BY_0 = 'by0'
    PLAYED_BY_1 = 'by1'
    PLAYED_BY_2 = 'by2'
    PLAYED_BY_3 = 'by3'
    TABLE_BY_1 = 'tb1'
    TABLE_BY_2 = 'tb2'
    TABLE_BY_3 = 'tb3'
    ALL_STATES = [PLAYED_BY_0,
                  PLAYED_BY_1,
                  PLAYED_BY_2,
                  PLAYED_BY_3,
                  TABLE_BY_1,
                  TABLE_BY_2,
                  TABLE_BY_3,
                  IN_HAND,
                  UNKNOWN]
    n_for_hokm=5
    n_each_hand=13
    SCORE_TO_WIN=7
