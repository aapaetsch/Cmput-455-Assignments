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
            self.weights = self.openFile('weights')

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



        # print(probs)
        # self.weights = {}
        # if self.selection == 'rr':
        #     if self.policy == 'random':
        #         for key in probs.keys():
        #             probs[key] = round(self.num_sim / (self.num_sim * len(legalMoves)),3)
        #     else:
        #         probSum = 0 
        #         for key in probs.keys():
        #             x = wins/len(legalMoves)*self.num_sim
        #             probs[key] = x
        #             probSum += x
        #         for key in probs.keys():
        #             probs[key] = probs[key]/probSum

        #<---NEED TO ADD THE THING.... probs for rr random forces even distro... need to send a valid dict to get a valid genmove rr random answer
        self.weights = {}
        return probs
        


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
        
        weight =  self.weights.get(addy)
        return weight

    def patternSimulation(self, state, move, toplay):
        tempState = state.copy()
        tempState.play_move(move, toplay)

        while True:
            cp = tempState.current_player
            legalMoves = self.generateLegalMoves(tempState, cp)
            if self.isTerminal(legalMoves):
                return self.evaluate(cp)

            #<---If we are not in a terminal state--->
            moves = self.getPatternMoves(tempState, cp, legalMoves)
            
            #<---Then we chose a move from moves--->
            '''
            if x <= v1:...
            elif x<= v1+...+vn for all moves
            '''
            playedMove = False
            if len(moves) != 0:
                prob = random.uniform(0,1)
                vn = 0 
                for possibleMove in moves.keys():
                    vn += moves[possibleMove]
                    if prob <= vn:
                        tempState.play_move(possibleMove, cp)
                        playedMove = True
                        break

            if not playedMove:
                tempState.play_move(self.randomMoveGen(tempState, cp), cp)

    def getPatternMoves(self, state, cp, legalMoves):
        #<----generate a pattern move--->
        moves = {}
        weightSum = 0 
        for move in legalMoves:
            moveWeight = self.getWeight(state, cp, move)
            if moveWeight != None:
                assert move not in moves.keys()
                assert state.board[move] == EMPTY
                moves[move] = moveWeight
                weightSum += moveWeight
        moves = {k:(v/weightSum) for k,v in moves.items()}
        return moves

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

    def openFile(self, fileName):
        weights = {}
        with open(fileName, 'r') as f:
            for line in f:
                item = line.split(' ')
                weights[int(item[0])] = float(item[1])
        return weights


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionNoGo3(Nogo(), board)
    con.start_connection()


if __name__=='__main__':
    run()
