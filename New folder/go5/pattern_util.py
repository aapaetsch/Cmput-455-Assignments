"""
pattern_util.py
Utility functions for rule based simulations.
"""

import numpy as np
from pattern import pat3set
import random

from board_util import GoBoardUtil, EMPTY, PASS, BORDER


class PatternUtil(object):

    @staticmethod
    def neighborhood_33(board, point):
        """
        Get the pattern around point.
        Returns
        -------
        patterns :
        Set of patterns in the same format of what michi pattern base provides. Please refer to pattern.py to see the format of the pattern.
        """
        positions = [point-board.NS-1, point-board.NS, point-board.NS+1,
                     point-1, point, point+1,
                     point+board.NS-1, point+board.NS, point+board.NS+1]

        pattern = ""
        for d in positions:
            if board.board[d] == board.current_player:
                pattern += 'X'
            elif board.board[d] == GoBoardUtil.opponent(board.current_player):
                pattern += 'x'
            elif board.board[d] == EMPTY:
                pattern += '.'
            elif board.board[d] == BORDER:
                pattern += ' '
        return pattern

    @staticmethod
    def generate_pattern_moves(board):
        """
        Generate a list of moves that match pattern.
        This only checks moves that are neighbors of the moves in the last two steps.
        See last_moves_empty_neighbors() in simple_board for detail.
        """
        color = board.current_player
        pattern_checking_set = board.last_moves_empty_neighbors()
        moves = []
        for p in pattern_checking_set:
            if (PatternUtil.neighborhood_33(board, p) in pat3set):
                assert p not in moves
                assert board.board[p] == EMPTY
                moves.append(p)
        return moves
    
    @staticmethod
    def filter_moves_and_generate(board, moves, check_selfatari):
        """
        Move filter function.
        """
        color = board.current_player
        while len(moves) > 0:
            candidate = random.choice(moves)
            if PatternUtil.filter(board, candidate, color, check_selfatari):
                moves.remove(candidate)
            else:
                return candidate
        return None
    
    @staticmethod
    def filter_moves(board, moves, check_selfatari):
        color = board.current_player
        good_moves = []
        for move in moves:
            if not PatternUtil.filter(board,move,color,check_selfatari):
                good_moves.append(move)
        return good_moves
    
    # return True if move should be filtered
    @staticmethod
    def filleye_filter(board, move, color):
        assert move != None
        return not board.is_legal(move, color) or board.is_eye(move, color)
    
    # return True if move should be filtered
    @staticmethod
    def selfatari_filter(board, move, color):
        return (  PatternUtil.filleye_filter(board, move, color)
                or PatternUtil.selfatari(board, move, color)
                )
    
    # return True if move should be filtered
    @staticmethod
    def filter(board, move, color, check_selfatari):
        if check_selfatari:
            return PatternUtil.selfatari_filter(board, move, color)
        else:
            return PatternUtil.filleye_filter(board, move, color)

    @staticmethod
    def selfatari(board, move, color):
        max_old_liberty = PatternUtil.blocks_max_liberty(board, move, color, 2)
        if max_old_liberty > 2:
            return False
        cboard = board.copy()
        # swap out true board for simulation board, and try to play the move
        isLegal = cboard.play_move(move, color)
        if isLegal:
            new_liberty = cboard._liberty(move, color)
            if new_liberty==1:
                return True
        return False
            
    @staticmethod
    def blocks_max_liberty(board, point, color, limit):
        assert board.board[point] == EMPTY
        max_lib = -1 # will return this value if this point is a new block
        neighbors = board._neighbors(point)
        for n in neighbors:
            if board.board[n] == color:
                num_lib = board._liberty(n, color)
                if num_lib > limit:
                    return num_lib
                if num_lib > max_lib:
                    max_lib = num_lib
        return max_lib
    
    @staticmethod
    def generate_move_with_filter(board, use_pattern, check_selfatari):
        """
        Arguments
        ---------
        check_selfatari: filter selfatari moves?
        Note that even if True, this filter only applies to pattern moves
        use_pattern: Use pattern policy?
        """
        move = None
        if use_pattern:
            moves = PatternUtil.generate_pattern_moves(board)
            move = PatternUtil.filter_moves_and_generate(board, moves,
                                                         check_selfatari)
        if move == None:
            move = GoBoardUtil.generate_random_move(board, board.current_player,True)
        return move
    
    @staticmethod
    def generate_all_policy_moves(board, pattern, check_selfatari):
        """
        generate a list of policy moves on board for board.current_player.
        Use in UI only. For playing, use generate_move_with_filter
        which is more efficient
        """
        if pattern:
            pattern_moves = []
            pattern_moves = PatternUtil.generate_pattern_moves(board)
            pattern_moves = PatternUtil.filter_moves(board, pattern_moves, check_selfatari)
            if len(pattern_moves) > 0:
                return pattern_moves, "Pattern"
        return GoBoardUtil.generate_random_moves(board, True), "Random"
            
    @staticmethod
    def playGame(board, color, **kwargs):
        """
        Run a simulation game according to give parameters.
        """
        komi = kwargs.pop('komi', 0)
        limit = kwargs.pop('limit', 1000)
        simulation_policy = kwargs.pop('random_simulation','random')
        use_pattern = kwargs.pop('use_pattern',True)
        check_selfatari = kwargs.pop('check_selfatari',True)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        nuPasses = 0
        for _ in range(limit):
            color = board.current_player
            if simulation_policy == 'random':
                move = GoBoardUtil.generate_random_move(board,color,True)
            elif simulation_policy == 'rulebased':
                move = PatternUtil.generate_move_with_filter(board,use_pattern,check_selfatari)
            else:
                assert simulation_policy == 'prob'
                move = PatternUtil.generate_move_with_feature_based_probs(board)
            board.play_move(move, color)
            if move == PASS:
                nuPasses += 1
            else:
                nuPasses = 0
            if nuPasses >= 2:
                break
        winner,_ = board.score(komi)
        return winner

    @staticmethod
    def generate_moves_with_feature_based_probs(board):
        from feature import Features_weight
        from feature import Feature
        assert len(Features_weight) != 0
        moves = []
        gamma_sum = 0.0
        empty_points = board.get_empty_points()
        color = board.current_player
        probs = np.zeros(board.maxpoint)
        all_board_features = Feature.find_all_features(board)
        for move in empty_points:
            if board.is_legal(move, color) and not board.is_eye(move, color):
                moves.append(move)
                probs[move] = Feature.compute_move_gamma(Features_weight, all_board_features[move])
                gamma_sum += probs[move]
        if len(moves) != 0:
            assert gamma_sum != 0.0
            for m in moves:
                probs[m] = probs[m] / gamma_sum
        return moves, probs
    
    @staticmethod
    def generate_move_with_feature_based_probs(board):
        moves, probs = PatternUtil.generate_moves_with_feature_based_probs(board)
        if len(moves) == 0:
            return None
        return np.random.choice(board.maxpoint, 1, p=probs)[0]
    
    @staticmethod
    def generate_move_with_feature_based_probs_max(board):
        """Used for UI"""
        moves, probs = PatternUtil.generate_moves_with_feature_based_probs(board)
        move_prob_tuple = []
        for m in moves:
            move_prob_tuple.append((m, probs[m]))
        return sorted(move_prob_tuple,key=lambda i:i[1],reverse=True)[0][0]
