#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_nogo3 import GtpConnectionNoGo3
from board_util import GoBoardUtil
from simple_board import SimpleGoBoard
from legalMoveGen import getLegalMoves


class Nogo():
    def __init__(self):
        """
        NoGo player that selects moves randomly 
        from the set of legal moves.
        Passe/resigns only at the end of game.

        """
        self.name = "NoGoAssignment2"
        self.version = 1.0
        
    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move(board, color, False)

    def simulate(self, board, move, toplay):
        pass

    def simulateMove(self, board, move, toplay):
        #<---simulation for a given move--->
        wins = 0 
        for _ in range(   ):
            result = self.simulate(board, move, toplay)
            if result == toplay:
                wins += 1
        return wins
        
    def get_move(self, board, color):
        tempBoard = board.copy()
        legalMoves = getLegalMoves(tempBoard)
        if not moves:
            return None

        legalMoves.append(None)
        pass
        #<---got to implememnt the two versions here --->



    
def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionNoGo3(Nogo(), board)
    con.start_connection()

def parse_args():
    #<---Not sure if this is needed--->
    pass


if __name__=='__main__':
    run()
