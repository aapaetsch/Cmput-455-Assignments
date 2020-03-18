

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

    # def policy_moves_cmd(self, args):
    #     color = self.board.current_player
    #     moveList = self.go_engine.getMoves(self.board, color)
    #     if moveList == None:
    #         self.respond()
    #     else:
    #         sortedList = {self.strPoint(k): v for k,v in sorted(moveList.items(), key=lambda item: self.strPoint(item[0]))}
    #         returnKey = [key for key in sortedList.keys()]
    #         returnValue = [str(sortedList[key]) for key in sortedList.keys()]
    #         self.respond('{} {}'.format(' '.join(returnKey), ' '.join(returnValue)))
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
            self.go_engine.weights = self.go_engine.openFile('weights')
            prob = self.go_engine.getPatternMoves(self.board, cp, legalMoves)
            self.go_engine.weights = {}
            probs = [[self.strPoint(k), round(v,3)] for k,v in sorted(prob.items(), key = lambda item: self.strPoint(item[0]))] 
            x = 0 
            for i in probs:
                x += i[1]
            print(x)
            self.respond('{} {}'.format(' '.join([pt for pt,v in probs]),' '.join([str(v) for pt,v in probs])))




    def genmove_cmd(self, args):
        assert args[0] == 'w' or args[0] == 'b'
        color = WHITE if args[0] == 'w' else BLACK
        moveDict = self.go_engine.getMoves(self.board, color)
        if moveDict == None:
            self.respond()
        else:
            move_return = self.strPoint(max(moveDict.items(), key=lambda item: item[1])[0])
            self.respond(move_return)


    def strPoint(self, point):
        return format_point(point_to_coord(point, self.board.size))



     