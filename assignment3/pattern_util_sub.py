'''
pattertn_util_sub.py
subclass of PatternUtil for changes needed in the assignment
'''

import numpy as np
from pattern import pat3set
import random
from board_util import EMPTY, PASS, BORDER
from pattern_util import PatternUtil
from board_util import GoBoardUtil as GBU

class PatternUtilNogo3(object):
	#<---in the playgame 

	'''
	PatternUtil.playGame(cboard, 
						opp,
						komi=self.komi,
						limit=self.limit,
						random_simulation=self.random_simulation,
						use_pattern=self.use_pattern
						check_selfataru=self.check_selfatari)
					'''
	#No clue what size and limit do
	#limit = num_sim 
	#policy = random or pattern
	#check self atari requires move_filter? not sure about this one yet
	@staticmethod
	def playGame(gameState, color, limit, policy):#<---Will have to add args here 
		
		random = 1 if policy == 'random' else 0

		nuPasses = 0 
		for _ in range(limit):
			c = gameState.current_player
			if random:
				move = GBU.generate_random_move(gameState, color, True)#<---I think this function is what needs to be changed to allow eyefilling moves... thought it was playGame

			else:
				#<---I think this is where the pattern based solver goes--->
				pass

			#<---This can be sped up if we assume all moves passed are legal (insert into board, change player)--->
			gameState.play_move(move, color)
#<----From here down needs to be changed for NoGo rules-->
			if move == PASS:
				nuPasses += 1 
			else:
				nuPasses = 0 
			if nuPasses >= 2:
				break
		winner, _ = board.score(komi)
		return winner
	#<------------------------->
