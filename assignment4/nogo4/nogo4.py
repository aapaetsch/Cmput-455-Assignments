from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY, BLACK, WHITE
from simple_board import SimpleGoBoard
import sys
import ucb
import numpy as np
import random 
from math import log, sqrt


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
        self.weights = self.openFile('nogo4/weights')
        self.UCB_ON = True
        self.best_move = None

    def openFile(self, fileName):
        weights = {}
        with open(fileName, 'r') as f:
            for line in f:
                item = line.split(" ")
                weights[int(item[0])] = float(item[1])
        return weights

    def evaluate(self, cp):
        return BLACK + WHITE - cp

    def isTerminal(self, remainingMoves):
        if len(remainingMoves) == 0:
            return True
        return False
    
    def undoMove(self, state, move):
        state.board[move] == EMPTY
        cp = state.current_player
        state.current_player = WHITE + BLACK - cp

    def quickPlayMove(self, state, move, player):
        state.board[move] = player
        state.current_player = WHITE + BLACK - player

    def generateLegalMoves(self, gameState, color):
        ePts = gameState.get_empty_points()
        moves = []
        for pt in ePts:
            if gameState.is_legal(pt, color):
                moves.append(pt)
        return moves

    def randomMoveGen(self, state, player):
        moves = state.get_empty_points()
        np.random.shuffle(moves)
        for move in moves:
            if state.is_legal(move, player):
                return move
        return None

    def getPatternMoves(self, state, cp, legalMoves):
        #<---generate a pattern move--->
        moves = {}
        weightSum = 0 
        for move in legalMoves:
            moveWeight = self.getWeight(state, cp, move)
            if moveWeight != None:
                assert move not in moves.keys()
                assert state.board[move] == EMPTY
                moves[move] = moveWeight
                weightSum += moveWeight
        return {k:(v/weightSum) for k,v in moves.items()}

    def getWeight(self, state,  toplay, m):
        pattern = [m+state.NS-1, m+state.NS, m+state.NS+1,
                   m-1,                      m+1,
                   m-state.NS-1, m-state.NS, m-state.NS+1]
        addy = 0 
        for i in range(len(pattern)):
            p = state.board[pattern[i]]
            if toplay == BLACK:
                addy += p *(4**i)
            else:
                addy += ((BLACK + WHITE - p)*(4**i)) if p == BLACK or p == WHITE else (p*(4**i))
        return self.weights.get(addy)

    def get_move(self, original_board, color):
        self.num_sim = 15

        tempState = original_board.copy()
        legalMoves = self.generateLegalMoves(tempState, color)
        bestScore = -float('inf')

        if len(legalMoves) == 0:
            return None
        
        if self.UCB_ON:
            C = 0.4
            stats = [[0,0] for _ in legalMoves]
            num_simulation = len(legalMoves) * self.num_sim
            for n in range(num_simulation):
                moveIndex = ucb.findBest(stats, C, n)
                result = self.simulate(tempState, legalMoves[moveIndex], color)
            
                
                stats[moveIndex][1] += 1
                if result == color:
                    stats[moveIndex][0] += 1

                self.best_move = [legalMoves,stats] 

            best = legalMoves[ucb.bestArm(stats)]
        

        return best

    def simulate(self, gameState, move, toplay):
        tempState = gameState.copy()
        tempState.play_move(move, toplay)
        
        while True:

            cp = tempState.current_player
            legalMoves = self.generateLegalMoves(tempState, cp)
            if self.isTerminal(legalMoves):
                return self.evaluate(cp)
            moves = self.getPatternMoves(tempState, cp, legalMoves)
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
                tempState.playMove(self.randomMoveGen(tempState, cp), cp)

            

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(Nogo(), board)
    con.start_connection()

if __name__=='__main__':
    run()
