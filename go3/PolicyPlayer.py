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

class PolicyPlayer():
    """
    Policy player that randomly chooses among all policy moves.
    """
    def __init__(self, sim_rule, move_filter):
        self.name = "PolicyPlayer"
        self.version = 1.0
        self.use_pattern = False if sim_rule == 'random' else True
        self.check_selfatari = move_filter
    
    def get_move(self, board, toplay):
        return PatternUtil.generate_move_with_filter(board, self.use_pattern, self.check_selfatari)

def run(sim_rule, move_filter):
    """
    Start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnectionGo3(PolicyPlayer(sim_rule, move_filter), board)
    con.start_connection()

def parse_args():
    """
    Parse the arguments of the program.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--simrule', type=str, default='random', help='type of simulation policy: random or rulebased')
    parser.add_argument('--movefilter', action='store_true', default=False, help='whether use move filter or not')

    args = parser.parse_args()
    sim_rule = args.simrule
    move_filter = args.movefilter

    if sim_rule != "random" and sim_rule != "rulebased":
        print('simrule must be random or rulebased')
        sys.exit(0)

    return sim_rule, move_filter

if __name__=='__main__':
    sim_rule, move_filter = parse_args()
    run(sim_rule, move_filter)

