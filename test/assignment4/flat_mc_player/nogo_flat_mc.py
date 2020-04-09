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

class NoGoFlatMC():
    def __init__(self):
        """
        NoGo player that selects moves by flat Monte Carlo Search.
        Resigns only at the end of game.

        """
        self.name = "NoGoFlatMC"
        self.version = 1.0
        self.simulations_per_move = 10
        self.best_move = None

    def simulate(self, board, toplay):
        """
        Run a simulated game for a given starting move.
        """
        res = game_result(board)
        simulation_moves = []
        while (res is None):
            move = GoBoardUtil.generate_random_move(board, board.current_player)
            play_move(board, move, board.current_player)
            simulation_moves.append(move)
            res = game_result(board)
        for m in simulation_moves[::-1]:
            undo(board, m)
        result = 1.0 if res == toplay else 0.0
        return result

    def get_move(self, original_board, color):
        """
        The genmove function using one-ply MC search.
        """
        board = original_board.copy()
        moves = GoBoardUtil.generate_legal_moves(board, board.current_player)
        toplay = board.current_player
        assert color == toplay
        best_result, best_move = -1.0, None
        best_move = moves[0]
        self.best_move = moves[0]
        wins = np.zeros(len(moves))
        visits = np.zeros(len(moves))
        for _ in range(self.simulations_per_move):
            for i, move in enumerate(moves):
                play_move(board, move, toplay)
                res = game_result(board)
                if res == toplay:
                    # This move is a immediate win
                    undo(board, move)
                    return move 
                sim_result = self.simulate(board, toplay)
                wins[i] += sim_result
                visits[i] += 1.0
                win_rate = wins[i] / visits[i]
                if win_rate > best_result:
                    best_result = win_rate
                    best_move = move 
                    self.best_move = move 
                undo(board, move)
            assert best_move is not None 
        return best_move

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(NoGoFlatMC(), board)
    con.start_connection()

if __name__=='__main__':
    run()
