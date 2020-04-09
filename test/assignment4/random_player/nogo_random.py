#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil
from simple_board import SimpleGoBoard

class NoGoRandom():
    def __init__(self):
        """
        NoGo player that selects moves randomly 
        from the set of legal moves.
        Resigns only at the end of game.

        """
        self.name = "NoGoRandom"
        self.version = 1.0
        
    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board, color)
    
def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(NoGoRandom(), board)
    con.start_connection()

if __name__=='__main__':
    run()
