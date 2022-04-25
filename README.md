# Self-taught AI agents playing a card game

This repository was my first attempt to train AI agents play card games. A zero-sum game in the co-operative competetive setting was selected and A2C and DQN agents were trained to play again MCTS agents. The MCTS idea is insipired by the famous AlphaGo paper.

The environment (the game), RL agents, and MCTS model were all developed from scratch.

The final results of the trained agents show a winning rate against the MCTS algorithm in more than 93% of cases. Given the characteristics of this game, the final outcome is heavily reliant on the random starting point and achieving 100% winning rate is almost impossible.

TODO for future:
1- Implement the punishment learning idea and see the effectiveness
