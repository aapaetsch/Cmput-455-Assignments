
"""
gtp_connection.py
Module for playing games of Go using GoTextProtocol

Parts of this code were originally based on the gtp module 
in the Deep-Go project by Isaac Henrion and Amos Storkey 
at the University of Edinburgh.
"""
import traceback
from sys import stdin, stdout, stderr
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, PASS, \
                       MAXSIZE, coord_to_point
import numpy as np
import re
import time
import random
import signal
from TranspositionTable import TT
alarmTime = 0
import os
import psutil


class TimeException(Exception):
    pass

def handler(signum, frame):
    alarmTIME = time.time()
    raise TimeException

signal.signal(signal.SIGALRM, handler)


class GtpConnection():

    def __init__(self, go_engine, board, debug_mode = False):
        """
        Manage a GTP connection for a Go-playing engine

        Parameters
        ----------
        go_engine:
            a program that can reply to a set of GTP commandsbelow
        board: 
            Represents the current board state.
        """
        self._debug_mode = debug_mode
        self.go_engine = go_engine
        self.board = board
        self.time_limit = 1
        self.originalPlayer = None
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "genmove": self.genmove_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "legal_moves": self.legal_moves_cmd,
            "gogui-rules_game_id": self.gogui_rules_game_id_cmd,
            "gogui-rules_board_size": self.gogui_rules_board_size_cmd,
            "gogui-rules_legal_moves": self.gogui_rules_legal_moves_cmd,
            "gogui-rules_side_to_move": self.gogui_rules_side_to_move_cmd,
            "gogui-rules_board": self.gogui_rules_board_cmd,
            "gogui-rules_final_result": self.gogui_rules_final_result_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd,
            "timelimit": self.time_limit_cmd,
            "solve": self.solve_cmd
        }

        # used for argument checking
        # values: (required number of arguments, 
        #          error message on argnum failure)
        self.argmap = {
            "boardsize": (1, 'Usage: boardsize INT'),
            "komi": (1, 'Usage: komi FLOAT'),
            "known_command": (1, 'Usage: known_command CMD_NAME'),
            "genmove": (1, 'Usage: genmove {w,b}'),
            "play": (2, 'Usage: play {b,w} MOVE'),
            "legal_moves": (1, 'Usage: legal_moves {w,b}'),
            "timelimit":(1, "Usage: timelimit INT")
        }
    
    def write(self, data):
        stdout.write(data) 

    def flush(self):
        stdout.flush()

    def start_connection(self):
        """
        Start a GTP connection. 
        This function continuously monitors standard input for commands.
        """
        line = stdin.readline()
        while line:
            self.get_cmd(line)
            line = stdin.readline()

    def get_cmd(self, command):
        """
        Parse command string and execute it
        """
        if len(command.strip(' \r\t')) == 0:
            return
        if command[0] == '#':
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]; args = elements[1:]
        if self.has_arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".
                               format(traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error('Unknown command')
            stdout.flush()

    def has_arg_error(self, cmd, argnum):
        """
        Verify the number of arguments of cmd.
        argnum is the number of parsed arguments
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg):
        """ Write msg to the debug stream """
        if self._debug_mode:
            stderr.write(msg)
            stderr.flush()

    def error(self, error_msg):
        """ Send error msg to stdout """
        stdout.write('? {}\n\n'.format(error_msg))
        stdout.flush()

    def respond(self, response=''):
        """ Send response to stdout """
        stdout.write('= {}\n\n'.format(response))
        stdout.flush()

    def reset(self, size):
        """
        Reset the board to empty board of given size
        """
        self.board.reset(size)

    def board2d(self):
        return str(GoBoardUtil.get_twoD_board(self.board))
        
    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond('2')

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the Go engine """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the  Go engine """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game with new boardsize args[0]
        """
        self.reset(int(args[0]))
        self.respond()

    def showboard_cmd(self, args):
        self.respond('\n' + self.board2d())

    def komi_cmd(self, args):
        """
        Set the engine's komi to args[0]
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if command args[0] is known to the GTP interface
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(' '.join(list(self.commands.keys())))

    def legal_moves_cmd(self, args):
        """
        List legal moves for color args[0] in {'b','w'}
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)

    def play_cmd(self, args):
        """
        play a move args[1] for given color args[0] in {'b','w'}
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            if board_color != "b" and board_color !="w":
                self.respond("illegal move: \"{}\" wrong color".format(board_color))
                return
            color = color_to_int(board_color)
            if args[1].lower() == 'pass':
                self.respond("illegal move: \"{} {}\" wrong coordinate".format(args[0], args[1]))
                return
            coord = move_to_coord(args[1], self.board.size)
            if coord:
                move = coord_to_point(coord[0],coord[1], self.board.size)
            else:
                self.error("Error executing move {} converted from {}"
                           .format(move, args[1]))
                return
            if not self.board.play_move(move, color):
                self.respond("illegal move: \"{} {}\" ".format(args[0], board_move))
                return
            else:
                self.debug_msg("Move: {}\nBoard:\n{}\n".
                                format(board_move, self.board2d()))
            self.respond()
        except Exception as e:
            self.respond('illegal move: \"{} {}\" {}'.format(args[0], args[1], str(e)))

    
    # def genmove_cmd(self, args):
    #    """
    #    Generate a move for the color args[0] in {'b', 'w'}, for the game of gomoku.
    #    """
    #    board_color = args[0].lower()
    #    color = color_to_int(board_color)
    #    move = self.go_engine.get_move(self.board, color)
    #    move_coord = point_to_coord(move, self.board.size)
    #    move_as_string = format_point(move_coord)
    #    if self.board.is_legal(move, color):
    #        self.board.play_move(move, color)
    #        self.respond(move_as_string)
    #    else:
    #        self.respond("resign")
     
    def genmove_cmd(self, args):
        """
        Generate a move for the color args[0] in {'b', 'w'}, for the game of gomoku.
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        #if game is not over
        if len(moves) > 0:
            ouput = self.solve_cmd(self.board)
            if output != "unkonwn" and ouput != "b" and output != "w": 
                output_move = ouput[2:]
                m = move_to_coord(output_move,self.board.size)
                move = self.board.pt(m[0],m[1])
                if self.board.is_legal(move, color):
                    self.board.play_move(move, color)
                    self.respond(ouptut_move)
                else:
                    self.respond("resign")
            else: #generate random move
                move = self.go_engine.get_move(self.board, color)
                move_coord = point_to_coord(move, self.board.size)
                move_as_string = format_point(move_coord)
                if self.board.is_legal(move, color):
                    self.board.play_move(move, color)
                    self.respond(move_as_string)
                else:
                    self.respond("resign")
        else:
            self.respond("resign")

    def gogui_rules_game_id_cmd(self, args):
        self.respond("NoGo")
    
    def gogui_rules_board_size_cmd(self, args):
        self.respond(str(self.board.size))
    
    def legal_moves_cmd(self, args):
        """
            List legal moves for color args[0] in {'b','w'}
            """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)

    def gogui_rules_legal_moves_cmd(self, args):
        empties = self.board.get_empty_points()
        color = self.board.current_player
        legal_moves = []
        for move in empties:
            if self.board.is_legal(move, color):
                legal_moves.append(move)

        gtp_moves = []
        for move in legal_moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)
    
    def gogui_rules_side_to_move_cmd(self, args):
        color = "black" if self.board.current_player == BLACK else "white"
        self.respond(color)
    
    def gogui_rules_board_cmd(self, args):
        size = self.board.size
        str = ''
        for row in range(size-1, -1, -1):
            start = self.board.row_start(row + 1)
            for i in range(size):
                point = self.board.board[start + i]
                if point == BLACK:
                    str += 'X'
                elif point == WHITE:
                    str += 'O'
                elif point == EMPTY:
                    str += '.'
                else:
                    assert False
            str += '\n'
        self.respond(str)
    
    def gogui_rules_final_result_cmd(self, args):
        empties = self.board.get_empty_points()
        color = self.board.current_player
        legal_moves = []
        for move in empties:
            if self.board.is_legal(move, color):
                legal_moves.append(move)
        if not legal_moves:
            result = "black" if self.board.current_player == WHITE else "white"
        else:
            result = "unknown"
        self.respond(result)

    def gogui_analyze_cmd(self, args):
        self.respond("pstring/Legal Moves For ToPlay/gogui-rules_legal_moves\n"
                     "pstring/Side to Play/gogui-rules_side_to_move\n"
                     "pstring/Final Result/gogui-rules_final_result\n"
                     "pstring/Board Size/gogui-rules_board_size\n"
                     "pstring/Rules GameID/gogui-rules_game_id\n"
                     "pstring/Show Board/gogui-rules_board\n"
                     )

    def undo(self, move, gameState):
        gameState.board[move] = EMPTY
        cp = gameState.current_player
        gameState.current_player = WHITE + BLACK - cp

    def skip_checks_play(self, move, color, gameState):
        gameState.board[move] = color
        gameState.current_player = WHITE + BLACK - color

    def time_limit_cmd(self, args):
        assert 1 <= int(args[0]) <= 100
        self.time_limit = int(args[0])

    def solve_cmd(self, args):
        self.builtin = []
        self.builtinTimes = []
        self.my = []
        self.myTimes = []
        signal.alarm(self.time_limit)

        self.originalPlayer = self.board.current_player
        rootState = self.board.copy()
        self.pValues = {}
        for move in range(len(rootState.board)):
            if rootState.board[move] != BORDER:
                self.pValues[move] = self.getP(move)
        
        try:
            self.rootTime = time.time()
            #<---init for transposition table--->
            self.maxSize = self.board.size * self.board.size
            self.zobrist_init(rootState) #<---self.hash is created in here
            self.tt = TT()
            stop = time.time()
            print('Transposition Table setup:', stop-self.rootTime)

            # #<---FOR LEGAL MOVE TESTING--->
            # legalMoveTime = time.time()
            # remainingMoves = GoBoardUtil.generate_legal_moves(rootState, self.originalPlayer)
            # self.builtinTimes.append(time.time()-legalMoveTime)
            # self.builtin.append(remainingMoves)

            # myTime = time.time()
            # myRemaining = self.getLegalMoves(rootState)
            # self.myTimes.append(time.time()-myTime)
            # self.my.append(myRemaining)

            # #<---done testing--->
            remainingMoves = self.getLegalMoves(rootState)
            remainingCount = len(remainingMoves)

            if self.isTerminal(remainingCount):
                #<---If a move is terminal right away, we assume we are in P-Position--->
                m = 'b' if self.originalPlayer == WHITE else 'w'
                self.respond(m)
                # self.comparison()#<___REMOVE LATER___>
                return m 
                # signal.alarm(0)
            else:
            
                minmaxResult = self.call_minMax(rootState, remainingMoves)
                if minmaxResult != False :
                    return minmaxResult
                    
            m = 'b' if self.originalPlayer == WHITE else 'w'
            self.respond(m)
            print('Total time:', time.time() - self.rootTime)
            signal.alarm(0)
            # self.comparison()#<___REMOVE LATER___>
            return m

        except:
            self.respond("unknown")
            print('total time before exit:', time.time() - self.rootTime, 'Timelimit:', self.time_limit)
            signal.alarm(0)
            # self.comparison()#<___REMOVE LATER___>
            return 'unknown'
            
        signal.alarm(0)

    def call_minMax(self, gameState, remainingMoves):
        for move in remainingMoves:
            start = time.time()

            oldHash = self.playMove(move, self.originalPlayer, gameState)

            isWin = self.minmax_bool_and(gameState)

            if isWin:
                winningColor = 'b' if self.originalPlayer == BLACK else 'w'
                winningMove = format_point(point_to_coord(move, self.board.size))
                response = '{} {}'.format(winningColor, winningMove.lower())
                self.respond(response)
                print('Total Time:', time.time() - self.rootTime )
                # self.comparison()
                return response
            self.undo(move, gameState)
            self.hash = oldHash
            print("Move:", format_point(point_to_coord(move,self.board.size)), 'Time:', time.time()-start)
            # self.comparison()
        return False


    #<---Trying to implement an and or version here --->
    def minmax_bool_or(self, gameState):
        #<---Check the transposition table if this node has been found --->
        result = self.tt.lookup(self.hash)
        if result != None:
            return result

        currentPlayer = gameState.current_player

       
        remainingMoves = self.getLegalMoves(gameState)
        remainingCount = len(remainingMoves)
        terminalState = self.isTerminal(remainingCount)
        if terminalState:
            return self.storeResult(self.hash, self.evaluation(currentPlayer, remainingCount))
        
        for move in remainingMoves:
            oldHash = self.playMove(move, currentPlayer, gameState)
            #<---call minmax AND node--->
            isWin = self.minmax_bool_and(gameState)
        
            #<---Revert the hash and gameState back to the previous value--->
            self.undo(move, gameState)
            self.hash = oldHash
            if isWin:
 
                return self.storeResult(self.hash, True)

        return self.storeResult(self.hash, False)


    def minmax_bool_and(self, gameState):
        #<---Check the transposition table if this node has been found--->
        result = self.tt.lookup(self.hash)
        if result != None:
            return result
            
        currentPlayer = gameState.current_player
        # #<---My testing--->
        # legalMoveTime = time.time()
        # remainingMoves = GoBoardUtil.generate_legal_moves(gameState, currentPlayer)
        # self.builtinTimes.append(time.time()-legalMoveTime)
        # self.builtin.append(remainingMoves)
        
        # myTime = time.time()
        # myRemaining = self.getLegalMoves(gameState)
        # self.myTimes.append(time.time()-myTime)
        # self.my.append(myRemaining)

        # #<---End of testing--->
        
        remainingMoves = self.getLegalMoves(gameState)
        remainingCount = len(remainingMoves)
        terminalState = self.isTerminal(remainingCount)
        if terminalState:
            return self.storeResult(self.hash, self.evaluation(currentPlayer, remainingCount))
        
        for move in remainingMoves:
            oldHash = self.playMove(move, currentPlayer, gameState)
            #<---Call minmax OR node--->
            isWin = self.minmax_bool_or(gameState)
        
            #<---Revert the hash and gameState back to the previous value--->
            self.undo(move, gameState)
            self.hash = oldHash
            if not isWin:
                return self.storeResult(self.hash, False)

        return self.storeResult(self.hash, True)

    def playMove(self, move, currentPlayer, gameState):
        #This method saves the current hash and returns it.
        #Does all the necessary steps to simulate playing a move. 
        oldHash = self.hash
        self.skip_checks_play(move, currentPlayer, gameState)
        p = self.pValues[move]
        self.updateHash(self.hash, self.zobristArray[p][currentPlayer], self.zobristArray[p][0])
        return oldHash

    def storeResult(self, newHash, result):
        self.tt.store(newHash, result)
        return result

    def getP(self,move):
        #<---takes a move and turns it into p without borders--->
        coord = point_to_coord(move, self.board.size)
        return (coord[1]-1)+(coord[0]-1)*self.board.size

    def updateHash(self, oldHash, XORin, XORout):
        self.hash = oldHash ^ XORin ^XORout

    def zobrist_init(self, gameState):
        # This method creates self.hash and self.zobristArray
        # prepares them for use

        #<--- populate the zobrist array with 3 random numbers per board space (3 possible states 0, 1, 2)--->
        self.zobristArray = []
        for _ in range(self.maxSize):
            self.zobristArray.append([random.getrandbits(64) for _ in range(3)])

        #<---Calculate the initial hash value of the board (ignores borders)--->
        self.hash = 0 
        count = 0 
        for point in gameState.board:
            if point != BORDER:
                if count == 0:
                    self.hash = self.zobristArray[count][point]
                else:
                    self.hash = self.hash ^ self.zobristArray[count][point]
                count += 1


    def evaluation(self ,currentPlayer, remainingMoves):
        if self.originalPlayer == currentPlayer:
            return False
        else:
            return True
        

    def isTerminal(self, remainingMoves):
        if remainingMoves != 0:
            return False
        else:
            return True 

    def getLegalMoves(self, gameState):
        #This method returns a list containing all of the legal moves for a game state
        moves = gameState.get_empty_points()
        cp = gameState.current_player
        opponent = BLACK + WHITE - cp
         
        legalMoves = []
        for m in moves:
            if self.checkMoveLegality(m, gameState, cp, opponent):
                legalMoves.append(m)
        return legalMoves
             
            
    def checkMoveLegality(self, m, tempState, cp, opponent):
        #This method checks if a move is legal. Skips and streamlines unnecessary steps in GoBoardUtil.generate_legal_moves
        neighbors = tempState.neighbors[m]
        totalNeighbors = len(neighbors)
        #check if it is surrounded 
        oppNeighbors = 0 
        allyNeighbors = 0 
        emptyNeighbors = 0 
        for n in neighbors:
            if tempState.board[n] == cp:
                allyNeighbors += 1               
            elif tempState.board[n] == opponent:
                oppNeighbors += 1 
            elif tempState.board[n] == EMPTY:
                emptyNeighbors += 1
        
        if (emptyNeighbors == totalNeighbors) or (oppNeighbors == 0 and emptyNeighbors > 0):
            return True
        
        elif oppNeighbors == totalNeighbors:
            return False

        if allyNeighbors > 0 and oppNeighbors == 0:
            if emptyNeighbors == 0:
                return self.detectLibertyInBlock(m, tempState, cp)
            else:
                return True

        elif oppNeighbors > 0:
            validNeighbors = emptyNeighbors 
            if allyNeighbors > 0:
                if self.detectLibertyInBlock(m, tempState, cp):
                    validNeighbors += allyNeighbors
            #<---check if there is valid opponent blocks--->
            tempState.board[m] = cp
            
            for n in neighbors:
                if tempState.board[n] == opponent:
                    if self.detectLibertyInBlock(n, tempState, opponent):
                        validNeighbors += 1
                    else:
                        tempState.board[m] = EMPTY
                        return False

            if validNeighbors == totalNeighbors:
                tempState.board[m] = EMPTY
                return True
            tempState.board[m] = EMPTY
            return False
        
        if tempState.is_legal(m, cp):
            return True
        return False

    def detectLibertyInBlock(self, m, tempState, player):
        visited = np.full(tempState.maxpoint, False, dtype=bool)
        #<---Detect if there is at least 1 liberty for my block--->
        stack = [m]
        visited[m] = True
        
        while stack:
            point = stack.pop()
            for nb in tempState.neighbors[point]:
                if not visited[nb]:
                    if tempState.board[nb] == player:
                        stack.append(nb)
                        visited[nb] = True
                    elif tempState.board[nb] == EMPTY:
                        
                        return True
        
        return False


    def comparison(self):
        sumBuiltinTime = sum(self.builtinTimes)
        denomBuiltIn = len(self.builtinTimes)
        sumMyTime = sum(self.myTimes)
        denomMyTime = len(self.myTimes)
        if denomMyTime != denomBuiltIn:
            print('Time denominators not equal')
        avgTimeBuiltIn = sumBuiltinTime/denomBuiltIn
        avgTimeMine = sumMyTime/denomMyTime
        print("Find Legal Moves Stats:\n\tBuilt in Time: {}\tMy Time:{}\tMy Savings:{}".format(str(avgTimeBuiltIn), str(avgTimeMine), str( (avgTimeBuiltIn-avgTimeMine)*denomBuiltIn ) ))
        notEqual = []
        for i in range(len(self.builtin)):
            if self.builtin[i] != self.my[i]:
                notEqual.append([self.builtin[i], self.my[i]])
        for i in range(len(notEqual)):
            print('\t', notEqual[i])
        print('\tTotal not equal: {}'.format(str(len(notEqual))))
     




def point_to_coord(point, boardsize):
    """
    Transform point given as board array index 
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)

def format_point(move):
    """
    Return move coordinates as a string such as 'a1', or 'pass'.
    """
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    #column_letters = "abcdefghjklmnopqrstuvwxyz"
    if move == PASS:
        return "pass"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1]+ str(row) 
    
def move_to_coord(point_str, board_size):
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return PASS
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            raise ValueError
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            raise ValueError
    except (IndexError, ValueError):
        # e.g. "a0"
        raise ValueError("wrong coordinate")
    if not (col <= board_size and row <= board_size):
        # e.g. "a20"
        raise ValueError("wrong coordinate")
    return row, col

def color_to_int(c):
    """convert character to the appropriate integer code"""
    color_to_int = {"b": BLACK , "w": WHITE, "e": EMPTY, 
                    "BORDER": BORDER}
    return color_to_int[c] 
