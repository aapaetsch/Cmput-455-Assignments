from board_util import BLACK, WHITE, BORDER, EMPTY, PASS
import numpy as np
def getLegalMoves(g, color):
    #<---Gets legal moves faster than builtin --->
    moves = g.get_empty_points()
    cp = color
    op = BLACK - WHITE - cp
    legalMoves = []

    for m in moves:
        if checkMoveLegality(m, g, cp, op):
            legalMoves.append(m)
    return legalMoves

def checkMoveLegality( m, s, cp, op):
    #<---Checks if a move (m) is legal in gameState (s) --->
    NB = s.neighbors[m]
    tNB = len(NB)

    opNB= 0
    cpNB = 0 
    eNB = 0 

    for n in NB:
        if s.board[n] == cp:
            cpNB += 1
        elif s.board[n] == op:
            opNB += 1
        elif s.board[n] == EMPTY:
            eNB += 1

    if (eNB == tNB) or (opNB == 0 and eNB > 0):
        return True
    
    elif opNB == tNB:
        return False
    
    
    if cpNB > 0 and opNB == 0:
        if eNB == 0:
            return detectLibertyInBlock(m, s, cp)
        return True
    
    elif opNB > 0:
        vNB = eNB
        #<---Check if there is a valid ally block--->
        if aNB > 0:
            if detectLibertyInBlock(m, s, cp):
                #<---All ally blocks are connected, only need 1 search for all ally neighbors (aNB)--->
                vNB += aNB

        #<---Check if there is a valid opponent block for each opponent neighbor (opNB)--->
        s.board[m] = cp
        for n in NB:
            if s.board[n] == op:
                if detectLibertyInBlock(n, s, op):
                    vNB += 1
                else:
                    s.board[m] = EMPTY
                    return False
        if vNB == tNB:
            s.board[m] = EMPTY
            return True

        s.board[m] = EMPTY
        return False

    if s.is_legal(m, cp):
        return True
    return False

def findConnectedNB( s, NBs: list, opponent: int ) -> list:
    #<---We can add this if we need a speed up--->
    pass


def detectLibertyInBlock( m, s, p):
    #<---Detects if a block has a liberty--->
    #<---move (m), gameState (s), player (p)--->
    v = np.full(s.maxpoint, False, dtype=bool)
    stack = [m]
    v[m] = True
    
    while stack:
        pt = stack.pop()
        for nb in s.neighbors[pt]:
            
            if not v[nb]:
            
                if s.board[nb] == p:
                    stack.append(nb)
                    v[nb] = True
                
                elif s.board[nb] == EMPTY:
                    return True
    return False