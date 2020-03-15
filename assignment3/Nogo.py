#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_nogo3 import GtpConnectionNoGo3
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY
from simple_board import SimpleGoBoard
from legalMoveGen import getLegalMoves
import sys
import ucb
import numpy as np
import random


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

    def randomSimulation(self, state, move, toplay):
        tempState = state.copy()
        #<---Play 1 game to the end from here--->
        self.quickPlayMove(tempState, move, toplay)
 
        while True:

            cp = tempState.current_player
            # legalMoves = getLegalMoves(tempState, cp)
            legalMoves = self.generateLegalMoves(tempState, cp)
            if self.isTerminal(legalMoves):
                return cp

            
            move = random.choice(legalMoves)
            self.quickPlayMove(tempState, move, cp)

    def patternSimulation(self, state, move, toplay):
        pass

    def quickPlayMove(self, state, move, player):
        state.board[move] = player
        state.current_player = WHITE + BLACK - player

    def undoMove(self, state, move):
        state.board[move] = EMPTY
        cp = state.current_player
        state.current_player = WHITE + BLACK - cp


    def simulate(self, state, move, toplay):
        if self.policy == 'random':
            return self.randomSimulation(state, move, toplay)
        else:
            return self.patternSimulation(state, move, toplay)



    def simulateMove(self, board, move, toplay):
        #<---simulation for a given move--->
        wins = 0 
        for _ in range(self.num_sim):
            result = self.simulate(board, move, toplay)
            if result == toplay:
                wins += 1
        return wins

    def getMoves(self, state, color):
        self.originalPlayer = color
        gameState = state.copy()
        # legalMoves = getLegalMoves(gameState, color)
        legalMoves = self.generateLegalMoves(gameState, color)
        probs = {}

        if not legalMoves:
            return None

        if self.selection == 'rr':
            #<---Do a round robin selection--->
            print('White' if color == WHITE else 'black')
            for move in legalMoves:
                wins = self.simulateMove(gameState, move, color)
                probs[move] = wins/self.num_sim

        else:
            #<---Do a UCB Selection--->
            C = 0.4
            stats = [[0,0] for _ in legalMoves] 
            num_simulation = len(legalMoves) * self.num_sim
            for n in range(num_simulation):
                moveIndex = ucb.findBest(stats, C, n)
                result = self.simulate(gameState, legalMoves[moveIndex], color)
                if result == toplay:
                    stats[moveIndex][0] += 1
                stats[moveIndex][1] += 1



        return probs
        
    def isTerminal(self, remainingMoves):
        if len(remainingMoves) == 0:
            return True
        return False

    def generateLegalMoves(self, gameState, color):
        ePts = gameState.get_empty_points()
        moves = []
        for pt in ePts:
            if gameState.is_legal(pt, color):
                moves.append(pt)
        return moves


# def byPercentage(pair):
#     return pair[1]

# def writeMoves(board, moves, c, numSimulations):
#     gtp_moves = []
#     for i in range(len(moves)):
#         if moves[i] != None:
#             x, y = point_to_coord(moves[i], board.size)
#             gtp_moves.append((format_point((x,y)), float(c[i])/float(numSimulations)))
#         else:
#             gtp_moves.append(('Pass',float(c[i])/float(numSimulations)))
#     sys.stderr.write("win rates: {}\n".format(sorted(gtp_moves, key=byPercentage, reverse=True)))
# sys.stderr.flush() #<---not sure why this is here??

# def select_best_move(board, moves, moveWins):
#     max_child = np.argmax(moveWins)
#     return moves[max_child]

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionNoGo3(Nogo(), board)
    con.start_connection()


if __name__=='__main__':
    run()
