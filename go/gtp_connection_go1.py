"""
gtp_connection_go1.py
Example for extending a GTP engine with extra commands
"""
from gtp_connection import GtpConnection

class GtpConnectionGo1(GtpConnection):

    def __init__(self, go_engine, board, debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine :
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        GtpConnection.__init__(self, go_engine, board, debug_mode)
        self.commands["hello"] = self.hello_cmd
        self.argmap["hello"] = (0, 'Usage: hello')

    def hello_cmd(self, args):
        """ Dummy Hello Command """
        self.respond("Hello! " + self.go_engine.name)
