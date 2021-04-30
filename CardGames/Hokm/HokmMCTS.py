import numpy as np

def HokmMCTS(memory, hand, possible_cards, n_mcts_sims = 100):
	''' Monte Carlo Tree Search for Hokm
	
	##TODO: Complete this code
	'''

	# probabilities = np.zeros(len(possible_cards))

	# for j in n_mcts_sims:

		# Create a deck

		# only keep the unknown cards from the memroy in the deck and remove the rest of them

		# instantiate the players with the deck and make them all play randomly (strategy = "random")

		# instantiate a new hokm table

		# set the hokm from memory to the new table

		# add the on_table cards on the table

		# update the turn

		# update the table

		# update anything else you think is necessary, like players' scores

		# play that specific round the player is about to decide

		# randomly select a card from possible_cards
		# selected_card = np.random.choice(possible_cards)
		# idx = possible_cards.index(selected_card)

		# then similar to what happend in run.py

		# while not hokm_table.game_over():

			# play rounds

		# if the player is winner, then add 1 to the probabilities
		# probabilities[idx] += 1

	# find the card with highest probability of winning and return it

	return np.random.choice(possible_cards)