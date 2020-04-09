#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection_go3 import GtpConnectionGo3
from gtp_connection import point_to_coord, format_point
from board_util import GoBoardUtil
from pattern_util import PatternUtil
from simple_board import SimpleGoBoard
import numpy as np
import argparse
import sys
from mcts import MCTS

def count_at_depth(node, depth, nodesAtDepth):
    if not node._expanded:
        return
    nodesAtDepth[depth] += 1
    for _,child in node._children.items():
        count_at_depth(child, depth+1, nodesAtDepth)

class Go5():
    def __init__(self, num_sim, sim_rule, move_filter, in_tree_knowledge, size=7, limit=100, exploration=0.4):
        """
        Player that selects a move based on MCTS from the set of legal moves
        """
        self.name = "Go5"
        self.version = 0.22
        self.komi = 6.5
        self.MCTS = MCTS()
        self.num_simulation = num_sim
        self.limit = limit
        self.exploration = exploration 
        self.simulation_policy = sim_rule
        self.use_pattern = True
        self.check_selfatari = move_filter
        self.in_tree_knowledge = in_tree_knowledge
        self.parent = None
    
    def reset(self):
        self.MCTS = MCTS()

    def update(self, move):
        self.parent = self.MCTS._root 
        self.MCTS.update_with_move(move)
    
    def get_move(self, board, toplay):
        move = self.MCTS.get_move(board,
                toplay,
                komi=self.komi,
                limit=self.limit,
                check_selfatari=self.check_selfatari,
                use_pattern=self.use_pattern,
                num_simulation = self.num_simulation,
                exploration = self.exploration,
                simulation_policy = self.simulation_policy,
                in_tree_knowledge = self.in_tree_knowledge)
        self.update(move)
        return move

    def get_node_depth(self, root):
        MAX_DEPTH = 100
        nodesAtDepth = [0] * MAX_DEPTH
        count_at_depth(root, 0, nodesAtDepth)
        prev_nodes = 1
        return nodesAtDepth
    
    def get_properties(self):
        return dict(
            version=self.version,
            name=self.__class__.__name__,
        )
 
def run(sim, sim_rule, move_filter, in_tree_knowledge):
    """
    Start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionGo3(Go5(num_sim, sim_rule, move_filter, in_tree_knowledge), board)
    con.start_connection()

def parse_args():
    """
    Parse the arguments of the program.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sim', type=int, default=300, help='number of simulations per move, so total playouts=sim*legal_moves')
    parser.add_argument('--simrule', type=str, default='random', help='type of simulation policy: random or rulebased or probabilistic')
    parser.add_argument('--movefilter', action='store_true', default=False, help='whether use move filter or not')
    parser.add_argument('--in_tree_knowledge', type=str, default='None', help='whether use move knowledge to initial a new node or not')
    args = parser.parse_args()

    num_sim = args.sim
    sim_rule = args.simrule
    move_filter = args.movefilter
    in_tree_knowledge = args.in_tree_knowledge

    if sim_rule != "random" and sim_rule != "rulebased" and sim_rule != "prob":
        print('simrule must be random or rulebased or prob')
        sys.exit(0)

    return num_sim, sim_rule, move_filter, in_tree_knowledge

if __name__=='__main__':
    num_sim, sim_rule, move_filter, in_tree_knowledge = parse_args()
    run(num_sim, sim_rule, move_filter, in_tree_knowledge)

