# loading dependencies
import time
import logging
from CardGames.utils import Logger
from CardGames.GamesSettings import HokmSettings
from CardGames.Hokm.HokmTable import HokmTable
from CardGames.Hokm.HokmPlayer import HokmPlayer
from CardGames.Deck import Deck


def test():
    logger = Logger(level=logging.WARNING)

    p0_total: int = 0
    p1_total: int = 0
    hakem = 0
    while (p0_total < 3) and (p1_total < 3):
        deck = Deck()

        p0 = HokmPlayer(name='Alex', deck=deck, settings=HokmSettings, strategy='random', logger = logger)
        p1 = HokmPlayer(name='Ryan', deck=deck, settings=HokmSettings, strategy='MCTS', logger = logger)
        p2 = HokmPlayer(name='Jimmy', deck=deck, settings=HokmSettings, strategy='random', logger = logger)
        p3 = HokmPlayer(name='Mathew', deck=deck, settings=HokmSettings, strategy='MCTS', logger = logger)

        hokm_table = HokmTable(p0, p1, p2, p3,
                               deck=deck,
                               hakem=hakem,
                               settings=HokmSettings,
                               logger=logger)
        hokm_table.initialize()

        n_round: int = 0
        p0_sum: int = 0
        p1_sum: int = 0

        start = time.time()
        while not hokm_table.game_over():
            n_round += 1
            print ("Round--------->", n_round)
            hokm_table.logger.info(f'\nRound {n_round} Starts \n')  # logging the player
            hokm_table.play_one_round(n_round=n_round)
            p0_sum = hokm_table.players[0].my_score
            p1_sum = hokm_table.players[1].my_score
            hokm_table.logger.info(
                f"\nGroup(0,2) Sum Score = {p0_sum} Group(1,3) Sum Score = {p1_sum}\n")  # logging the player

            # print (p0_sum, p1_sum)
            # winner = 0 if p0_sum >= p1_sum else 1

        print ("########--------", time.time()-start)

        if p0_sum > p1_sum:
            p0_total += 1
        else:
            p1_total += 1
        hokm_table.logger.critical(
            f"\n P0_total= {p0_total} , P1_total = {p1_total}\n")  # logging the player

        if (p0.my_score > p0.other_score and hakem in [1, 3]) or \
                (p1.my_score > p1.other_score and hakem in [0, 2]):
            
            hakem = (hakem + 1) %4

        # input()

    if p0_total > p1_total:
        hokm_table.logger.info(
            f"\n{p0.name} and {p2.name} Wins the Game with Total Score = {p0_total} to {p1_total}\n")
        # logging the player
        print(f"\n{p0.name} and {p2.name} Wins the Game with Total Score = {p0_total} to {p1_total}\n")
        # logging the player
    else:
        hokm_table.logger.info(
            f"\n{p1.name} and {p3.name} Wins the Game with Total Score = {p1_total} to {p0_total}\n")
        # logging the player
        print(f"\n{p1.name} and {p3.name} Wins the Game with Total Score = {p1_total} to {p0_total}\n")
        # logging the player


if __name__ == "__main__":
    test()
