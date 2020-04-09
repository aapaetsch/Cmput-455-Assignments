"""
gtp_connection_go3.py
Example for extending a GTP engine with extra commands
"""
from gtp_connection import GtpConnection, point_to_coord, format_point
from pattern_util import PatternUtil
from board_util import GoBoardUtil

def sorted_point_string(points, boardsize):
    result = []
    for point in points:
        x, y = point_to_coord(point, boardsize)
        result.append(format_point((x, y)))
    return ' '.join(sorted(result))

class GtpConnectionGo3(GtpConnection):

    def __init__(self, go_engine, board, debug_mode = False):
        """
        GTP connection of Go3
        """
        GtpConnection.__init__(self, go_engine, board, debug_mode)
        
        self.commands["selfatari"] = self.selfatari_cmd
        self.commands["use_pattern"] = self.use_pattern_cmd
        self.commands["random_simulation"] = self.random_simulation_cmd
        self.commands["use_ucb"] = self.use_ucb_cmd
        self.commands["num_sim"] = self.num_sim_cmd
        self.commands["legal_moves_for_toPlay"] = self.legal_moves_for_toPlay_cmd
        self.commands["policy_moves"] = self.policy_moves_cmd
        self.commands["random_moves"] = self.random_moves_cmd
        self.commands["gogui-analyze_commands"] = self.gogui_analyze_cmd

        self.argmap["selfatari"] = (1, 'Usage: selfatari BOOL')
        self.argmap["use_pattern"] = (1, 'Usage: use_pattern BOOL')
        self.argmap["random_simulation"] = (1, 'Usage: random_simulation BOOL')
        self.argmap["use_ucb"] = (1, 'Usage: use_ucb BOOL')
        self.argmap["num_sim"] = (1,'Usage: num_sim #(e.g. num_sim 100 )')

    def get_parameter_cmd(self, args):
        pars = self.go_engine.get_pars()
        self.respond(pars)
    
    def selfatari_cmd(self, args):
        valid_values = [False,True]
        value = bool(int(args[0]))
        if value not in valid_values:
            self.error('Argument ({}) must be True or False'.format(value))
        self.go_engine.check_selfatari = value
        self.respond()
    
    def use_pattern_cmd(self, args):
        valid_values = [False,True]
        value = bool(int(args[0]))
        if value not in valid_values:
            self.error('Argument ({}) must be True or False'.format(value))
        self.go_engine.use_pattern = value
        self.go_engine.random_simulation = not value
        self.respond()
    
    def use_ucb_cmd(self, args):
        valid_values = [False,True]
        value = bool(int(args[0]))
        if value not in valid_values:
            self.error('Argument ({}) must be True or False'.format(value))
        self.go_engine.use_ucb = value
        self.respond()
    
    def random_simulation_cmd(self, args):
        valid_values = [False,True]
        value = bool(int(args[0]))
        if value not in valid_values:
            self.error('Argument ({}) must be True or False'.format(value))
        self.go_engine.random_simulation = value
        self.go_engine.use_pattern = not value
        self.respond()
    
    def num_sim_cmd(self, args):
        self.go_engine.sim = int(args[0])
        self.respond()

    def policy_moves_cmd(self, args):
        """
        Return list of policy moves for the current_player of the board
        """
        policy_moves, type_of_move = PatternUtil.generate_all_policy_moves(self.board,
                                                        self.go_engine.use_pattern,
                                                        self.go_engine.check_selfatari)
        if len(policy_moves) == 0:
            self.respond("Pass")
        else:
            response = type_of_move + " " + sorted_point_string(policy_moves, self.board.size)
            self.respond(response)

    def random_moves_cmd(self, args):
        """
        Return list of random moves (legal, but not eye-filling)
        """
        moves = GoBoardUtil.generate_random_moves(self.board, True)
        if len(moves) == 0:
            self.respond("Pass")
        else:
            self.respond(sorted_point_string(moves, self.board.size))

    def legal_moves_for_toPlay_cmd(self, args):
        try:
            color= self.board.current_player
            moves = GoBoardUtil.generate_legal_moves(self.board, color)
            gtp_moves = []
            for move in moves:
                coords = point_to_coord(move, self.board.size)
                gtp_moves.append(format_point(coords))
            sorted_moves = ' '.join(sorted(gtp_moves))
            self.respond(sorted_moves)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def gogui_analyze_cmd(self, args):
        try:
            self.respond("pstring/Legal Moves For ToPlay/legal_moves_for_toPlay\n"
                         "pstring/Policy Moves/policy_moves\n"
                         "pstring/Random Moves/random_moves\n"
                         )
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))
