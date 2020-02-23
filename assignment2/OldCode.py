 def minmax_bool_or(self, gameState, depth):
        #<---Check the transposition table if this node has been found --->
        result = self.tt.lookup(self.hash)
        if result != None:
            return result

        currentPlayer = gameState.current_player
        remainingMoves = GoBoardUtil.generate_legal_moves(gameState, currentPlayer)
        
        if self.isTerminal(remainingMoves):
            return self.storeResult(self.hash, self.evaluation(currentPlayer))

        for move in remainingMoves:
            gameState.skip_checks_play(move, currentPlayer)

            #<-- updating the hash value --->
            p = self.pValues[move]
            self.updateHash(self.hash, self.zobristArray[p][currentPlayer], self.zobristArray[p][0])

            #<---call minmax AND node--->
            isWin = self.minmax_bool_and(gameState)
        
            #<---Revert the hash and gameState back to the previous value--->
            gameState.undo(move)
            self.updateHash(self.hash, self.zobristArray[p][0], self.zobristArray[p][currentPlayer])
            
            if isWin:
                # self.mirror(gameState, True)
                return self.storeResult(self.hash, True)

        # self.mirror(gameState, False)
        return self.storeResult(self.hash, False)


    def minmax_bool_and(self, gameState, depth):
        #<---Check the transposition table if this node has been found--->
        result = self.tt.lookup(self.hash)
        if result != None:
            return result

        currentPlayer = gameState.current_player
        remainingMoves = GoBoardUtil.generate_legal_moves(gameState, currentPlayer)

        if self.isTerminal(remainingMoves):
            return self.storeResult(self.hash, self.evaluation(currentPlayer))
        
        for move in remainingMoves:
            gameState.skip_checks_play(move, currentPlayer)
            
            #<-- updating the hash value --->
            p = self.pValues[move]
            self.updateHash(self.hash, self.zobristArray[p][currentPlayer], self.zobristArray[p][0])

            #<---Call minmax OR node--->
            isWin = self.minmax_bool_or(gameState)
        
            #<---Revert the hash and gameState back to the previous value--->
            gameState.undo(move)
            self.updateHash(self.hash, self.zobristArray[p][0], self.zobristArray[p][currentPlayer])

            if not isWin:
                # self.mirror(gameState, False)
                return self.storeResult(self.hash, False)

        # self.mirror(gameState, True)
        return self.storeResult(self.hash, True)