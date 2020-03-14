# Cmput 455 sample code
# UCB algorithm
# Written by Martin Mueller

from math import log,sqrt
import sys
from gtp_connection import point_to_coord, format_point

INFINITY = float('inf')

def mean(stats, i):
    return stats[i][0] / stats[i][1]
    
def ucb(stats, C, i, n):
    if stats[i][1] == 0:
        return INFINITY
    return mean(stats, i)  + C * sqrt(log(n) / stats[i][1])

def findBest(stats, C, n):
    best = -1
    bestScore = -INFINITY
    for i in range(len(stats)):
        score = ucb(stats, C, i, n) 
        if score > bestScore:
            bestScore = score
            best = i
    assert best != -1
    return best

def bestArm(stats): # Most-pulled arm
    best = -1
    bestScore = -INFINITY
    for i in range(len(stats)):
        if stats[i][1] > bestScore:
            bestScore = stats[i][1]
            best = i
    assert best != -1
    return best

# tuple = (move, percentage, wins, pulls)
def byPercentage(tuple):
    return tuple[1]

# tuple = (move, percentage, wins, pulls)
def byPulls(tuple):
    return tuple[3]

def writeMoves(board, moves, stats):
    gtp_moves = []
    for i in range(len(moves)):
        if moves[i] != None:
            x, y = point_to_coord(moves[i], board.size)
            pointString = format_point((x,y))
        else:
            pointString = 'Pass'
        if stats[i][1] != 0:
            gtp_moves.append((pointString,
                            stats[i][0]/stats[i][1],
                            stats[i][0],
                            stats[i][1]))
        else:
            gtp_moves.append((pointString,
                            0.0,
                            stats[i][0],
                            stats[i][1]))
    sys.stderr.write("Statistics: {}\n"
                     .format(sorted(gtp_moves, key = byPulls,
                                               reverse = True)))
    sys.stderr.flush()

def runUcb(player, board, C, moves, toplay):
    stats = [[0,0] for _ in moves]
    num_simulation = len(moves) * player.sim
    for n in range(num_simulation):
        moveIndex = findBest(stats, C, n)
        result = player.simulate(board, moves[moveIndex], toplay)
        if result == toplay:
            stats[moveIndex][0] += 1 # win
        stats[moveIndex][1] += 1
    bestIndex = bestArm(stats)
    best = moves[bestIndex]
    writeMoves(board, moves, stats)
    return best

