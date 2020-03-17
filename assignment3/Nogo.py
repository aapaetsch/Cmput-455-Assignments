#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_nogo3 import GtpConnectionNoGo3
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER
from simple_board import SimpleGoBoard
from legalMoveGen import getLegalMoves
import sys
import ucb
import numpy as np
import random
from pattern_util import PatternUtil
from pattern import pat3set

def openFile(fileName):
    weights = {}
    with open(fileName, 'r') as f:
        for line in f:
            item = line.split(' ')
            weights[int(item[0])] = float(item[1])
    return weights

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
        tempState.play_move(move, toplay)
        while True:
            cp = tempState.current_player
            move = self.randomMoveGen(tempState, cp)
            if move == None:
                return self.evaluate(cp)
            tempState.play_move(move, cp)

    def randomMoveGen(self, state, player):
        moves = state.get_empty_points()
        np.random.shuffle(moves)
        for move in moves:
            legal = state.is_legal(move, player)
            if legal:
                return move
        return None

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


    def simulateMove(self, state, move, toplay):
        #<---simulation for a given move--->
        wins = 0 

        for _ in range(self.num_sim):
            result = self.simulate(state, move, toplay)
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

        if self.policy == 'pattern':
            self.weights = openFile('weights')

        if self.selection == 'rr':
            #<---Do a round robin selection--->
            print('White' if color == WHITE else 'black')
            for move in legalMoves:
                wins = self.simulateMove(gameState, move, color)
                # probs[move] = round(wins/(len(legalMoves)*self.num_sim),3)
                probs[move] = wins

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

        self.weights = {}
        if self.selection == 'rr':
            if self.policy == 'random':
                for key in probs.keys():
                    probs[key] = round(self.num_sim / (self.num_sim * len(legalMoves)),3)
            else:
                probSum = 0 
                for key in probs.keys():
                    x = wins/len(legalMoves)*self.num_sim
                    probs[key] = x
                    probSum += x
                for key in probs.keys():
                    probs[key] = probs[key]/probSum

        #<---NEED TO ADD THE THING.... probs for rr random forces even distro... need to send a valid dict to get a valid genmove rr random answer
        return probs
        
    def isTerminal(self, remainingMoves):
        if len(remainingMoves) == 0:
            return True
        return False

    def evaluate(self, cp):
        return BLACK + WHITE - cp

    def generateLegalMoves(self, gameState, color):
        ePts = gameState.get_empty_points()
        moves = []
        for pt in ePts:
            if gameState.is_legal(pt, color):
                moves.append(pt)
        return moves

    def getWeight(self, state,  toplay, move):
        pattern = PatternUtil.neighborhood_33(state, move)
        pattern = pattern[:4] + pattern[5:]#Get rid of point p 
        addy = 0 
        index = 0 
        for i in pattern:
            if i == 'X':
                addy += toplay * pow(4, index)
            
            elif i == 'x':
                addy += (BLACK + WHITE - toplay) * pow(4, index)
                
            elif i == '.':
                addy += EMPTY * pow(4, index)

            elif i == ' ':
                addy += BORDER * pow(4, index)
            index += 1 
        return self.weights[addy]        

    def patternSimulation(self, state, move, toplay):
        tempState = state.copy()
        tempState.play_move(move, toplay)

        while True:
            cp = tempState.current_player
            legalMoves = self.generateLegalMoves(tempState, cp)
            if self.isTerminal(legalMoves):
                return self.evaluate(cp)

            # #<---generate pattern moves--->
            # pattern_checking_set = tempState.last_moves_empty_neighbors()
            # moves = []
            # for p in pattern_checking_set:
            #     if (PatternUtil.neighborhood_33(tempState, p) in pat3set):
            #         assert p not in moves
            #         assert board.board[p] == EMPTY
            #         moves.append(p)
            # #<---Move by weight--->
            #<---Probably doing this wrong...
            weightedMax = 0 
            weightedMove = None
            for move in legalMoves:
                # weightedMoves[move] = self.getWeight(tempState, cp, move) 
                weight = self.getWeight(tempState, cp, move)
                if weight >= weightedMax:
                    weightedMax = weight
                    weightedMove = move

            tempState.play_move(weightedMove, cp)



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
