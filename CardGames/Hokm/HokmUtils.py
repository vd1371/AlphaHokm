

def analyze_round(played_cards, hokm, n_players):
		'''Who won this round?
		The player with the highest value wins the round
		If anyone plays any hokm card, the highest hokm card wins the round
		input: dict of  # key: card, value( i = the i th played card, turn = by global player number)
		'''
		first = True
		for card in played_cards:
			# For the first player
			if first:
				first_card_type = card.type
				highest_card = card
				first = False

			elif card.type == hokm:  # This act is called "Cutting"
				if hokm != highest_card.type:  # Boridan for the first time
					highest_card = card
				elif (card.number) > (highest_card.number):  # Boridan va Sar kardan
					highest_card = card
			# Comply with the table
			elif ((highest_card.type == card.type) and (card.number > highest_card.number)):
				highest_card = card

		# Finding winner's index
		winner = played_cards[highest_card][1]
		other_winner = (winner + 2) % n_players

		return winner, other_winner