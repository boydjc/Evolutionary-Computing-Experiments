import random
from math import sqrt

class ParseTree():

	def __init__(self):
		pass

	@staticmethod
	def full(depth_limit=0, current_depth=0):

		if not(current_depth == depth_limit):
			node = ParseTree.getOperatorNode()

			node.left = ParseTree.full(depth_limit, current_depth+1)
			node.right = ParseTree.full(depth_limit, current_depth+1)

		elif(current_depth >= depth_limit):
			node = ParseTree.getSensorNode()

		return node

	@staticmethod
	def grow(depth_limit=0, current_depth=0):

		if not(current_depth == depth_limit):
			randChoice = random.randint(0, 1)
			if(randChoice == 0):
				node = ParseTree.getOperatorNode()

				node.left = ParseTree.grow(depth_limit, current_depth+1)
				node.right = ParseTree.grow(depth_limit, current_depth+1)

			elif(randChoice == 1):
				node = ParseTree.getSensorNode()

		elif(current_depth >= depth_limit):

			node = ParseTree.getSensorNode()

		return node

	@staticmethod
	def getOperatorNode():
		# choose random operator node if we are not at the max depth
		operator_inputs = ['+', '-', '*', '/', 'RAND']
		rand_operator = operator_inputs[random.randint(0, len(operator_inputs)-1)]

		new_node = Node()
		new_node.value = rand_operator
		new_node.left = Node()
		new_node.right = Node()

		return new_node

	@staticmethod
	def getSensorNode():
		sensor_inputs = ['G', 'P', 'W', 'F', 'M', '#.#']
		rand_sensor = sensor_inputs[random.randint(0, len(sensor_inputs)-1)]

		if(rand_sensor == "#.#"):
			rand_sensor = round(random.uniform(9, -9),1)

		new_node = Node()
		new_node.value = rand_sensor

		return new_node

class Node():
	def __init__(self):
		self.value = None
		self.left = None
		self.right = None

	def execute(self, player, state, cache=None):
		# Sensor decisions
		if(self.value == 'G'):
			if('ghostDist' in cache):
				return cache['ghostDist'], cache
			else:
				gDist, cache = self.ghostDist(player, state, cache)

				return gDist, cache

		elif(self.value == 'P'):
			if('pillDist' in cache):
				return cache['pillDist'], cache
			else:
				pDist, cache =  self.pillDist(player, state, cache)

				return pDist, cache

		elif(self.value == 'W'):
			if('numOfWalls' in cache):
				return cache['numOfWalls'], cache
			else:
				 numWalls, cache = self.numOfAdjWalls(player, state, cache)

				 return numWalls, cache
		elif(self.value == 'F'):
			if('fruitDist' in cache):
				return cache['fruitDist'], cache
			else:
				fDist, cache = self.fruitDist(player, state, cache)

				return fDist, cache
		elif(self.value == 'M'):
			if('minPlayerDist' in cache):
				return cache['minPlayerDist'], cache
			else:
				playerDist, cache = self.playerDist(player, state, cache)

				return playerDist, cache
		elif(isinstance(self.value, float)):
			return self.value, cache

		# Operator decisions
		elif(self.value == '+'):
			leftResult, cache = self.left.execute(player, state, cache)

			rightResult, cache = self.right.execute(player, state, cache)

			opResult = leftResult + rightResult

			return opResult, cache
		elif(self.value == '-'):
			leftResult, cache = self.left.execute(player, state, cache)

			rightResult, cache = self.right.execute(player, state, cache)

			opResult = leftResult - rightResult

			return opResult, cache
		elif(self.value == '*'):
			leftResult, cache = self.left.execute(player, state, cache)

			rightResult, cache = self.right.execute(player, state, cache)

			opResult = leftResult * rightResult

			return opResult, cache
		elif(self.value == '/'):
			try:
				leftResult, cache = self.left.execute(player, state, cache)

				rightResult, cache = self.right.execute(player, state, cache)

				opResult = leftResult / rightResult

				return opResult, cache	
			except:
				return 0, cache
		elif(self.value == 'RAND'):
			leftResult, cache = self.left.execute(player, state, cache)

			rightResult, cache = self.right.execute(player, state, cache)

			opResult = random.uniform(leftResult, rightResult)

			return opResult, cache

	def ghostDist(self, player, state, cache):
		pacPlayerLocation = None
		ghostLocations = []

		for key, value in state['players'].items():
			if(player in key):
				pacPlayerLocation = state['players'][key]
			else:
				ghostLocations.append(state['players'][key])

		manhattanDistances = []

		for ghostLoc in ghostLocations:

			manhattanDistances.append(sum(abs(val1-val2) for val1, val2 in zip(pacPlayerLocation, ghostLoc)))

		minimumDistance = min(manhattanDistances)

		# store in cache for future use
		cache.update({'ghostDist': minimumDistance})

		return minimumDistance, cache


	def pillDist(self, player, state, cache):
		pacPlayerLocation = None
		pillLocations = state['pills']

		for key, value in state['players'].items():
			if(key == player):
				pacPlayerLocation = state['players'][key]

		manhattanDistances = []

		for pillLoc in pillLocations:

			manhattanDistances.append(sum(abs(val1-val2) for val1, val2 in zip(pacPlayerLocation, pillLoc)))

		minimumDistance = min(manhattanDistances)

		cache.update({'pillDist' : minimumDistance})

		return minimumDistance, cache

	def numOfAdjWalls(self, player, state, cache):
		pacPlayerLocation = None

		for key, value in state['players'].items():
			if(key == player):
				pacPlayerLocation = state['players'][key]

		walls = state['walls']

		numberOfWalls = 0

		if(pacPlayerLocation[0] == 0 or pacPlayerLocation[0] == len(walls)-1):
			# checking if we are on the first or last row of the map
			# if so we have to count the end of the map as a wall
			#print('Player at either top or bottom of map')
			numberOfWalls += 1
		
		if not pacPlayerLocation[0] == 0:
			# check above the player
			#print('Checking above the player')
			#print('Element above player: ', walls[pacPlayerLocation[0]-1][pacPlayerLocation[1]])
			if(walls[pacPlayerLocation[0]-1][pacPlayerLocation[1]] == 1):
				numberOfWalls += 1

		if not pacPlayerLocation[0] == len(walls)-1:
			# check under the player
			#print('Checking under player')
			#print('Element under player: ', walls[pacPlayerLocation[0]+1][pacPlayerLocation[1]])
			if(walls[pacPlayerLocation[0]+1][pacPlayerLocation[1]] == 1):
				numberOfWalls += 1

		# checking for the sides of the map here
		if(pacPlayerLocation[1] == 0 or pacPlayerLocation[1] == len(walls[0])-1):
			#print('Player at either far left or far right of map')
			numberOfWalls += 1

		if not pacPlayerLocation[1] == 0:
			#print('Checking to the left of player')
			#print('Element to left of player: ', walls[pacPlayerLocation[0]][pacPlayerLocation[1]-1])
			if(walls[pacPlayerLocation[0]][pacPlayerLocation[1]-1] == 1):
				numberOfWalls += 1

		if not pacPlayerLocation[1] == len(walls[0])-1:
			#print('Checking to the right of player')
			#print('Element to right of player: ', walls[pacPlayerLocation[0]][pacPlayerLocation[1]+1])
			if(walls[pacPlayerLocation[0]][pacPlayerLocation[1]+1] == 1):
				numberOfWalls += 1

		#print('Number of Adjacent Walls: ', numberOfWalls)

		cache.update({'numOfWalls': numberOfWalls})

		return numberOfWalls, cache


	def fruitDist(self, player, state, cache):
		if(state['fruit']):
			pacPlayerLocation = None

			for key, value in state['players'].items():
				if(key == player):
					pacPlayerLocation = state['players'][key]

			fruitDistance = sum(abs(val1-val2) for val1, val2 in zip(pacPlayerLocation, state['fruit']))

			cache.update({'fruitDist': fruitDistance})

			return fruitDistance, cache

		else:

			cache.update({'fruitDist': 0})
			return 0, cache

	def playerDist(self, player, state, cache):

		thisPlayerLocation = None

		for key, value in state['players'].items():
			if(key == player):
				thisPlayerLocation = state['players'][key]

		pacPlayerLocations = [state['players'][key] for key in state['players'].keys() if 'm' in key and not key == player]


		playerDistances = []

		for locCount in range(len(pacPlayerLocations)):
			playerDistances.append(sum(abs(val1-val2) for val1, val2 in zip(thisPlayerLocation, pacPlayerLocations[locCount])))

		try:
			minPlayerDistance = min(playerDistances)
		except:
			minPlayerDistance = 0

		cache.update({'minPlayerDist': minPlayerDistance})

		return minPlayerDistance, cache



