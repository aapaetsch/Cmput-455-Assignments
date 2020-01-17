#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_go1 import GtpConnectionGo1
from board_util import GoBoardUtil
from simple_board import SimpleGoBoard

class Go1():
    def __init__(self):
        """
        Go player that selects moves randomly from the set of legal moves.
        However, it filters eye-filling moves.
        Passes only if there is no other legal move.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go1"
        self.version = 1.0
        
    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board, color, True)
    

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionGo1(Go1(), board)
    con.start_connection()

if __name__=='__main__':
    run()
