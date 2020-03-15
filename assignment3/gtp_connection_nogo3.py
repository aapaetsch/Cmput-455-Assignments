

from legalMoveGen import getLegalMoves
from gtp_connection import GtpConnection, point_to_coord, format_point
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, PASS, MAXSIZE, coord_to_point
BLACK = 1
WHITE = 2

class GtpConnectionNoGo3(GtpConnection):

    def __init__(self, go_engine, board, debug_mode=False):

        GtpConnection.__init__(self, go_engine, board, debug_mode)

        self.commands["policy"] = self.policy_cmd
        self.commands["selection"] = self.selection_cmd
        self.commands["policy_moves"] = self.policy_moves_cmd
        self.commands["num_sim"] = self.num_sim_cmd

        self.argmap["policy"] = (1, "Usage: policy {random, pattern}")
        self.argmap["selection"] = (1, "Usage: selection {rr, ucb}")
        self.argmap["num_sim"] = (1, "Usage: num_sim INT")

    def num_sim_cmd(self, args):
        assert int(args[0])
        self.go_engine.num_sim = int(args[0])
        self.respond()

    def selection_cmd(self, args):
        assert args[0] == 'rr' or args[0] == 'ucb'
        self.go_engine.selection = args[0]
        self.respond()

    def policy_cmd(self, args):
        assert args[0] == 'random' or args[0] == 'pattern'
        self.go_engine.policy = args[0]
        self.respond()

    def policy_moves_cmd(self, args):
        "
        moves = getLegalMoves()
        movelist = []
        returnstring = ""
        for move in moves:
            move = GtpConnection.format_point(move)
            movelist.append(move)
            returnstring = returnstring + move + " "
        movelist.sort()
        probabilities = []
        #for move in movelist:
            #get prob
            #prob.append(prob)
            #returnstring = returnstring + prob + " "
            # """
        #pass
        moveList = self.go_engine.getMoves(self.board, self.board.current_player)
        moves = []
        probs = []
        for move in sorted(moveList):
            moves.append(move)
            probs.append(moveList[move])
        returnstring = ""
        for move in moves:
            returnstring = returnstring + str(move) + " "

        for prob in probs:
            returnstring = returnstring + str(round(prob,3)) + " "

        self.go_engine.policy_moves = returnstring
        self.respond()


    def genmove_cmd(self, args):
        pass
        self.go_engine.genmove
        self.respond()