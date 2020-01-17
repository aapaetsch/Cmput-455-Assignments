#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

import cProfile
import numpy as np
import random
from Go1 import Go1
from board_util import PASS, GoBoardUtil
from simple_board import SimpleGoBoard

def play_moves():
    """
    play 100 random games for profiling.
    """
    size = 7
    board = SimpleGoBoard(size)
    player = Go1()
    for _ in range(100): # play 100 games
        board.reset(size)
        nuPasses = 0
        while nuPasses < 2: # two passes in a row = end of game
            color = board.current_player
            move = player.get_move(board, color)
            board.play_move(move, color)
            if move == PASS:
                nuPasses += 1
            else:
                nuPasses = 0
    
random.seed(1)
np.random.seed(1)
cProfile.run("play_moves()")
