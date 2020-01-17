#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

import unittest
import numpy as np
from gtp_connection import GtpConnection
from board_util import BLACK, WHITE, EMPTY, BORDER, PASS, where1d,\
     GoBoardUtil
from simple_board import SimpleGoBoard

class MockGoEngine:
    def __init__(self):
        """
        Go player that selects moves randomly from the set of legal moves.
        Does not use the fill-eye filter.
        Passes only if there is no other legal move.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Mock"
        self.version = 1.234
        
    def get_move(self, board, color):
        return board.pt(1,1)
        
class GtpConnectionTestCase(unittest.TestCase):
    """Tests for simple_board.py"""

    def test_size_2(self):
        board = SimpleGoBoard(2)
        con = GtpConnection(Go0(), board)
        con.start_connection()


"""Main"""
if __name__ == '__main__':
    unittest.main()
