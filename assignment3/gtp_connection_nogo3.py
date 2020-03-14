


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
        pass


    def genmove_cmd(self, args):
        pass