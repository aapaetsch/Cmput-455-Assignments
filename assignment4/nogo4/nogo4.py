from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY, BLACK, WHITE
from simple_board import SimpleGoBoard

import numpy as np
import random 

def undo(board, move):
    board.board[move] = EMPTY
    board.current_player = GoBoardUtil.opponent(board.current_player)

def play_move(board, move, color):
    board.play_move(move, color)

def game_result(board):    
    legal_moves = GoBoardUtil.generate_legal_moves(board, board.current_player)
    if not legal_moves:
        result = BLACK if board.current_player == WHITE else WHITE
    else:
        result = None
    return result

class Nogo():
    def __init__(self):
        """
        NoGo player that selects moves by flat Monte Carlo Search.
        Resigns only at the end of game.
        Replace this player's algorithm by your own.

        """
        self.name = "NoGo Assignment 4"
        self.version = 1.0
        self.num_sim = 10
        self.weights = self.openFile('weights')

        self.simulations_per_move = 10
    
    def quickPlayMove(self, state, move, player)

    

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(NoGoFlatMC(), board)
    con.start_connection()

if __name__=='__main__':
    run()
