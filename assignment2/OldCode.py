def solve_cmd(self, args):
        self.flag = False
        self.originalPlayer = self.board.current_player
   
        rootState = self.board.copy()
        remainingMoves = GoBoardUtil.generate_legal_moves(rootState, self.originalPlayer)
        tt = TT()

        self.generateRandomForZobrist(rootState)

        if self.isTerminal(remainingMoves):
            self.respond('b' if self.originalPlayer == WHITE else 'w')
        
        else:
            for move in remainingMoves:
                rootState.play_move(move, self.originalPlayer)

                coord = point_to_coord(move, self.board.size)
                p = (coord[1]-1) + (coord[0]-1) * self.board.size
                self.hash = self.hash ^ self.zobristArray[p][self.originalPlayer]^self.zobristArray[p][0] 
                
                isWin = self.negamax_boolean(rootState, tt)

                if  isWin:
                    #the current player wins with this move, end here
                    winningColor = 'b' if self.originalPlayer == BLACK else 'w'
                    winningMove = format_point(point_to_coord(move, self.board.size))
                    self.respond('{} {}'.format(winningColor, winningMove.lower()))
                    self.flag = True
                rootState.undo(move)
                self.hash = self.hash ^ self.zobristArray[p][self.originalPlayer] ^ self.zobristArray[p][0]


        if not self.flag:
            #otherwise the opponent wins
            self.respond('b' if self.originalPlayer == WHITE else 'w')

    # def solve_cmd(self, args):
    #     self.flag = False
    #     self.originalPlayer = self.board.current_player
    #     rootState = self.board.copy()

    #     #<---This is for transposition tables--->
    #     tt = TT()
    #     self.generateRandomForZobrist(rootState)

    #     #<---Init negamax --->
    #     result =  self.negamax_boolean(rootState, tt)

    #     print(result)

    def negamax_boolean(self, gameState, tt):
        result = tt.lookup(self.hash)
        if result != None:
            return result
        
        currentPlayer = gameState.current_player
        remainingMoves = GoBoardUtil.generate_legal_moves(gameState, currentPlayer)
        
        if self.isTerminal(remainingMoves):
            return self.storeResult(tt, gameState, self.evaluation(currentPlayer))

        for move in remainingMoves:
            gameState.play_move(move, currentPlayer)

            coord = point_to_coord(move, self.board.size)
            p = (coord[1]-1) + (coord[0]-1) * self.board.size
            self.hash = self.hash ^ self.zobristArray[p][currentPlayer]^self.zobristArray[p][0] 
            
            value = not self.negamax_boolean(gameState, tt)
            print(move,'move')
            gameState.undo(move)

            self.hash = self.hash ^ self.zobristArray[p][currentPlayer] ^ self.zobristArray[p][0]
            # print(currentPlayer, gameState.current_player, 'herhe')
            if value:
                return self.storeResult(tt, gameState, True)
        
        return self.storeResult(tt, gameState, False)

    def generateRandomForZobrist(self, gameState): 
        # self.zobristArray = np.zeros(self.board.size * self.board.size, dtype=np.int64)
        # print(hash = random.getrandbits(64))
        self.zobristArray = []

        for i in range(self.board.size * self.board.size):
            self.zobristArray.append([random.getrandbits(64) for i in range(3)])
        self.hash = 0 
        count = 0 
        for point in gameState.board:
            if point != BORDER:
                self.hash = self.hash ^ self.zobristArray[count][point]
                count += 1
        print(self.zobristArray)


    def storeResult(self, tt, gameState, result):
        # This method stores a gamestate and its result in the transposition table, returns the result
        tt.store(self.hash, result)
        return result


    
    def evaluation(self, currentPlayer):
        #This method returns true if player ToPlay played the winning move
        if self.originalPlayer != currentPlayer:
            return True
        else:
            return False
        

    def isTerminal(self, remainingMoves):
        # This method returns true if the game is in a terminal state
        if len(remainingMoves) == 0:
            return True
        else:
            return False