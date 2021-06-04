#Loading dependencies
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Input, concatenate
from keras.models import Model
from keras.regularizers import l1, l2
import keras.backend as K
import keras.losses

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDRegressor

class DQN:

	def __init__(self):
		pass

	def predict(self, *args, **kawrgs):
		return np.random.choice(kawrgs['possible_actions'])
