# Loading dependencies
import ast
import os, sys
import numpy as np

# from learning models import your learning model
# from feature transformers import your feature transformer
# from utils import bucket

from RLUtils import Bucket
from FeatureTransformers.FT import *
import LearningModels.DQN as dqn


def initialize_learning(warm_up=False):
    # hyps = {}
    # Initialize the hyperparameters
    if warm_up:
        hyps = ast.literal_eval((open('WarmUpParams.txt', 'r').readlines()[0]))
    # Load model
    # {'t0': 112.26000000002053, 't1': 0.1, 'it': 1112683, 'n_pmodel_trained': 1206483, 'n_hmodel_trained': 0, 'lr': 0.0001}
    else:
        hyps = {
            't0': 112.26000000002053,
            't1': 0.1,
            'it': 1112683,
            'n_sim': 10000,
            'n_pmodel_trained': 1206483,
            'n_hmodel_trained': 0,
            'lr': 0.0001
        }
    # Create new model
    model = dqn(_for='Playing', _type='SGD', warm_up=False, n_trained=0)
    return hyps, model


def go_one_episode(table, ft, model, target_model, bucket, eps, gamma):
    # Reset tables
    # S: ft.encode(s_a)

    # It playes one episode
    # Gets the information from the players
    # Transform those information into expected vectors
    # add them to the bucket
    pmodel = dqn
    done = False
    while not done:
        table.reset(ft.episode, ft.hakem)
        initial_hand, hokm = table.initialize()
        # Play one episode
        n_round = 0
        while not table.game_over():
            n_round += 1
            table.play_one_round(n_round=n_round)

            # For in players:
            # for in n_rounds:
            # get the state, actions, and reward
            # Add to the bucket

            if not round == n_round:
                next_knowledge = p.memory[round + 1][STATE]
                next_played_card = p.memory[round + 1][ACTION]
                next_Q = pmodel.predict(ft.transform(next_knowledge, next_played_card))
            else:
                next_Q = 0

            Q = r + gamma * next_Q
            x = ft.transform(knowledge, played_card)
            x_y_dict[idx] = (x, Q)


def learn(warm_up=False):
    hyps, model = initialize_learning(warm_up)
    # _, target_model = initialize_learning(True)

    bucket = Bucket()

    # Create a table
    for it in range(hyps['n_sim']):

        go_one_episode(table, ft, model, target_model, bucket, hyps['eps'], hyps['gamma'])

        if bucket.ready():
            # Memory learning

            # Empty the bucket

            # save the model

            # upadate the target model
            _, target_model = initialize_learning(True)

        # Updating the epsilon
        if it % 100:
            hyps['t'] = hyps['t'] + hyps['eps_decay']

        # Monitoring the performance
        if it % 10:
    # Show some stats about the game and the progress