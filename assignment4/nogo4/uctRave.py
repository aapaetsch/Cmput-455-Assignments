from gtp_connection import GtpConnection, point_to_coord, format_point
from board_util import GoBoardUtil, EMPTY, BLACK, WHITE
from simple_board import SimpleGoBoard
import sys
import ucb
import numpy as np
import random 
from math import log, sqrt
PASS = 'pass'


def uct_val(node, child, exploration, max_flag): 
    if child._n_visits == 0:
        return float("inf")
    if max_flag:
        return float(child._black_wins)/child._n_visits + exploration*np.sqrt(np.log(node._n_visits)/child._n_visits)
    else:
        return float(child._n_visits - child._black_wins)/child._n_visits + exploration*np.sqrt(np.log(node._n_visits)/child._n_visits)

def generateLegalMoves(gameState, color):
        ePts = gameState.get_empty_points()
        moves = []
        for pt in ePts:
            if gameState.is_legal(pt, color):
                moves.append(pt)
        return moves

class Nogo():
    def __init__(self):
        self.name = "NoGo Assignment 4"
        self.version = 1.0
        self.weights = self.openFile('nogo4/weights')
        self.best_move = None
        self.parent = None
        self.num_sim = 10
        self.MCTS = MCTS(self.weights)

    def reset(self):
        self.MCTS = MCTS(self.weights)

    def update(self, move):
        self.parent = self.MCTS._root
        self.MCTS.update_with_move(move)

    def openFile(self, fileName):
        weights = {}
        with open(fileName, 'r') as f:
            for line in f:
                item = line.split(" ")
                weights[int(item[0])] = float(item[1])
        return weights
    

    def get_move(self, board, toplay):
        legalMoves = generateLegalMoves(board, toplay)
        num_simulation = len(legalMoves)* self.num_sim
        move = self.MCTS.get_move(board, toplay, num_simulation)
        self.update(move)
        return move


#exploration = 0.4


class MCTS(object):
    
    def __init__(self, weights):
        self._root  = TreeNode(None)
        self.toplay = BLACK
        self.exploration = 0.4
        self.weights = weights

    def get_move(self, board, toplay, num_simulation):

        if self.toplay != toplay:
            self._root = TreeNode(None)
        for n in range(num_simulation):
            print('playout')
            self._playout(board.copy(), toplay)
        moves_ls = [(move, node._n_visits) for move, node in self._root._children.items()]

        if not moves_ls:
            return None
        move = sorted(moves_ls, key=lambda i:i[1], reverse=True)[0]
        if move[0] == PASS:
            return None
        assert board.is_legal(move[0], toplay)
        return move[0]

    def _playout(self, board, color):
        
        node = self._root 
        # This will be True olny once for the root
        if not node._expanded:
            print('\texpand')
            node.expand(board, color)
        print('before while')
        while not node.is_leaf():
            print('\twhile not leaf')
            # Greedily select next move.                
            max_flag = color == BLACK
            move, next_node = node.select(self.exploration,max_flag)
            print('\tselected')
            
            board.play_move(move, color)
            color = BLACK + WHITE - color
            node = next_node
            print('end of loop')
        print(node.is_leaf(), color, board.current_player)
        assert node.is_leaf()
        if not node._expanded:
            node.expand(board, color)

        assert board.current_player == color
        leaf_value = self._evaluate_rollout(board, color)  
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(leaf_value)

    def _evaluate_rollout(self, board, toplay):
        print('rollout')
        winner = self.simulate(board, toplay)
        print('dinner',winner)
        if winner == BLACK:
            return 1
        else:
            return 0

    def simulate(self, board, toplay):
        tempState = gameState.copy()

        while True:
            cp = tempState.current_player
            legalMoves = generateLegalMoves(tempState, cp)
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

    def evaluate(self, cp):
        return BLACK + WHITE - cp

    def isTerminal(self, remainingMoves):
        if len(remainingMoves) == 0:
            return True
        return False




    def update_with_move(self, last_move):
        """
        Step forward in the tree, keeping everything we already know about the subtree, assuming
        that get_move() has been called already. Siblings of the new root will be garbage-collected.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
        else:
            self._root = TreeNode(None)
        self._root._parent = None
        self.toplay = BLACK + WHITE - self.toplay

    def point_to_string(self, board_size, point):
        if point == None:
            return 'Pass'
        x, y = point_to_coord(point, board_size)
        return format_point((x, y))







class TreeNode(object):
    """
    A node in the MCTS tree.
    """
    version = 0.22
    name = "MCTS Player"
    def __init__(self, parent):
        """
        parent is set when a node gets expanded
        """
        self._parent = parent
        self._children = {}  # a map from move to TreeNode
        self._n_visits = 0
        self._black_wins = 0
        self._expanded = False
        self._move = None

    def expand(self, board, color):
        """
        Expands tree by creating new children.
        """
        moves = board.get_empty_points()
        for move in moves:
            if move not in self._children:
                if board.is_legal(move, color):
                    self._children[move] = TreeNode(self)
                    self._children[move]._move = move
        self._children[PASS] = TreeNode(self)
        self._children[PASS]._move = PASS
        self._expanded = True


    def select(self, exploration, max_flag):
        """
        Select move among children that gives maximizes UCT. 
        If number of visits are zero for a node, value for that node is infinite, so definitely will get selected

        It uses: argmax(child_num_black_wins/child_num_vists + C * sqrt(2 * ln * Parent_num_vists/child_num_visits) )
        Returns:
        A tuple of (move, next_node)
        """
        return max(self._children.items(), key=lambda items:uct_val(self, items[1], exploration, max_flag))
        
    def update(self, leaf_value):
        """
        Update node values from leaf evaluation.
        Arguments:
        leaf_value -- the value of subtree evaluation from the current player's perspective.
        
        Returns:
        None
        """
        self._black_wins += leaf_value
        self._n_visits += 1

    def update_recursive(self, leaf_value):
        """
        Like a call to update(), but applied recursively for all ancestors.

        Note: it is important that this happens from the root downward so that 'parent' visit
        counts are correct.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(leaf_value)
        self.update(leaf_value)


    def is_leaf(self):
        """
        Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(Nogo(), board)
    con.start_connection()

if __name__=='__main__':
    run()
