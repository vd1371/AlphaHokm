#Loading dependencies
import numpy as np

class DQL:

	def __init__(self):
		pass

	def predict(self, *args, **kawrgs):
		return np.random.choice(kawrgs['possible_actions'])
