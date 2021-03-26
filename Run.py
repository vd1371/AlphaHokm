# loading dependencies
from CardGames import HokmTable
from CardGames import HokmPlayer
from CardGames import Deck
from CardGames import HokmSettings

def test():

	deck = Deck()

	p0 = HokmPlayer(name='Alex', deck=deck, settings=HokmSettings)
	p1 = HokmPlayer(name='Ryan', deck=deck, settings=HokmSettings)
	p2 = HokmPlayer(name='Jimmy', deck=deck, settings=HokmSettings)
	p3 = HokmPlayer(name='Mathew', deck=deck, settings=HokmSettings)

	hokm_table = HokmTable(p0, p1, p2, p3,
							deck = deck,
							hakem = 0,
							settings = HokmSettings)
	hokm_table.initialize()
	input()
	for _ in range(7):
		n_round = 0
		while not myHokmTable.game_over():
			n_round += 1
			myHokmTable.play_one_round(n_round = n_round)
			p0_sum = table.players[0].score
			p1_sum = table.players[1].score
			print (p0_sum, p1_sum)
			winner = 0 if p0_sum >= p1_sum else 1


if __name__ == "__main__":
	test()