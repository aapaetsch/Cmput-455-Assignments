

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
        cp = self.board.current_player
        legalMoves = self.go_engine.generateLegalMoves(self.board, cp)
        if self.go_engine.policy == 'random':
            #<---Do the probability calculations for random--->
            remainingMoves = len(legalMoves)
            if remainingMoves == 0:
                self.respond()
            else:
                prob = str(round(self.go_engine.num_sim / (self.go_engine.num_sim * remainingMoves), 3))

                self.respond('{} {}'.format(' '.join(sorted([self.strPoint(move) for move in legalMoves])), ' '.join([prob for i in range(remainingMoves)])))
        else:
            #<---Do the probability calculations for pattern--->
            prob = self.go_engine.getPatternMoves(self.board, cp, legalMoves)
            probs = [[self.strPoint(k), round(v,3)] for k,v in sorted(prob.items(), key = lambda item: self.strPoint(item[0]))] 
            self.respond('{} {}'.format(' '.join([pt for pt,v in probs]),' '.join([str(v) for pt,v in probs])))




    def genmove_cmd(self, args):
        assert args[0] == 'w' or args[0] == 'b'
        color = WHITE if args[0] == 'w' else BLACK
        bestMove, probs = self.go_engine.getMoves(self.board, color)
        if self.go_engine.selection == 'rr':
            print({self.strPoint(k):v for k,v in probs.items()})
        self.respond(self.strPoint(bestMove))


    def strPoint(self, point):
        return format_point(point_to_coord(point, self.board.size))



     