#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_nogo3 import GtpConnectionNoGo3
from board_util import GoBoardUtil
from simple_board import SimpleGoBoard
from legalMoveGen import getLegalMoves
import sys
import ucb


class Nogo():
    def __init__(self):
        """
        NoGo player that selects moves randomly 
        from the set of legal moves.
        Passe/resigns only at the end of game.

        """
        self.name = "NoGoAssignment2"
        self.version = 1.0
        self.policy = "random" # random or pattern
        self.selection = "rr" # rr or ucb
        self.num_sim = 10 # 10 is default
        

    def simulate(self, board, move, toplay):
        tempBoard = board.copy()
        #<---Play move can be optimized if this is slow --->
        tempBoard.play_move(move, toplay)
        opp = BLACK + WHITE - toplay
        #return PatternUtil.playGame(tempBoard, opp, ...)


    def simulateMove(self, board, move, toplay):
        #<---simulation for a given move--->
        wins = 0 
        for _ in range(self.num_sim):
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
        #<---Selection policy--->
        if self.selection == 'rr':
            #<---Round Robin--->
            moveWins = []
            for m in legalMoves:
                wins = self.simulateMove(tempBoard, m, color)
                moveWins.append(wins)
            writeMoves(tempBoard, legalMoves, moveWins, self.num_sim)
            return select_best_move(tempBoard, legalMoves, moveWins)

        else:
            #<---UCB runs from ucb.py--->
            C = 0.4 
            best = ucb.runUcb(self, tempBoard, C, legalMoves, color)
            return best
            




def byPercentage(pair):
    return pair[1]

def writeMoves(board, moves, c, numSimulations):
    gtp_moves = []
    for i in range(len(moves)):
        if moves[i] != None:
            x, y = point_to_coord(moves[i], board.size)
            gtp_moves.append((format_point((x,y)), float(c[i])/float(numSimulations)))
        else:
            gtp_moves.append(('Pass',float(c[i])/float(numSimulations)))
    sys.stderr.write("win rates: {}\n".format(sorted(gtp_moves, key=byPercentage, reverse=True)))
sys.stderr.flush() #<---not sure why this is here??

def select_best_move(board, moves, moveWins):
    max_child = np.argmax(moveWins)
    return moves[max_child]

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionNoGo3(Nogo(), board)
    con.start_connection()


if __name__=='__main__':
    run()
