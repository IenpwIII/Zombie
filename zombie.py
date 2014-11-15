import random
import time

def dirOffset(loc,direction):
	"""takes a numpad direction and an x,y coordinate pair. returns a new coordinate pair, offset by 1 in the specified direction"""
	if direction == 1:
		toX = loc[0] + 1
		toY = loc[1] - 1
	elif direction == 2:
		toX = loc[0] + 1
		toY = loc[1] 
	elif direction == 3:
		toX = loc[0] + 1
		toY = loc[1] + 1
	elif direction == 4:
		toX = loc[0] 
		toY = loc[1] - 1
	elif direction == 5:
		toX = loc[0]
		toY = loc[1]
	elif direction == 6:
		toX = loc[0] 
		toY = loc[1] + 1
	elif direction == 7:
		toX = loc[0] - 1
		toY = loc[1] - 1
	elif direction == 8:
		toX = loc[0] - 1
		toY = loc[1] 
	elif direction == 9:
		toX = loc[0] - 1
		toY = loc[1] + 1
	else:
		return loc

	newCoords = [toX,toY]
	return newCoords


class TerrainType(object):
	"""Each type of terrain gets one instance of this class which is referenced when tile information is needed.
	Icon = what's displayed on the map
	Defence = 
	Movement = number of action points required to move onto that type of terrain"""
	def __init__(self, icon, defence, movement):
		super(TerrainType, self).__init__()
		self.icon = icon
		self.defence = defence
		self.movement = movement

		

class Map(object):
	"""Units go on these. There is one main one in each game. There may be other minor ones (spirit realms, underground, etc).
	Each map has an x and a y dimension, and has four layers -- one each for terrain, buildings, and units... and other"""
	def __init__(self, xsize, ysize):
		super(Map, self).__init__()
		self.xsize = xsize
		self.ysize = ysize
		# create the data structure
		self.data = {"ground" : [],
					 "buildings" : [],
					 "other" : [],
					 "units" : []}
		for i in self.data:
			for x in xrange(self.xsize):
				self.data[i].append([])
				for y in xrange(self.ysize):
					self.data[i][x].append(None)

	# fill the map with one type of tile (units and buildings unaffected).
	def generateFlat(self,terrain):
		for x in xrange(self.xsize):
			for y in xrange(self.ysize):
				self.data["ground"][x][y] = terrain

	# go through the four layers displaying the first of unit, other, building, terrain, that exists for a given tile
	def dispMap(self):
		toDisp = []
		# figure out what thing's icon is to be displayed
		for x in xrange(self.xsize):
			for y in xrange(self.ysize):
				if self.data["units"][x][y] != None:
					toDisp.append(self.data["units"][x][y])
				elif self.data["other"][x][y] != None:
					toDisp.append(self.data["other"][x][y])	
				elif self.data["buildings"][x][y] != None:
					toDisp.append(self.data["buildings"][x][y])
				else:
					toDisp.append(self.data["ground"][x][y])
		# display all the icons in a grid
		for i in xrange(self.ysize):
			toPrint = []
			for j in xrange(self.xsize):
				toPrint.append(toDisp[self.xsize*i+j].icon)
			print "".join(toPrint)

	def updateTile(self,layer,loc,value):
		self.data[layer][loc[0]][loc[1]] = value

		

class Unit(object):
	"""This is the basic unit class. All units will be instances of Unit with stats drawn from external data.
	Icon = the image displayed by the Map
	Uclass = the unit's class
	Name = what to call the unit. Often the same as Uclass
	Realm = which Map the unit is on
	Domain = land/sea/air/etc.
	AP = number of action points allotted to the unit per turn
	Position = where the unit is located on the map
	AI = ai controlled? 1 = yes"""
	def __init__(self, icon, uclass, name, realm, team, position, ap, ai):
		super(Unit, self).__init__()
		self.icon = icon
		self.uclass = uclass
		self.name = name
		self.realm = realm
		self.team = team
		self.position = position
		self.maxap = ap
		self.ai = ai
		# add the unit to its team
		self.team.addMember(self,self.name)
		# place the unit on the map
		self.changeLoc(self.position)

	# "teleport" the unit to a new location on the map. This sets the old unit location to None and OVERWRITES any existing unit information
	def changeLoc(self,loc):
		self.realm.updateTile("units",self.position,None)
		self.realm.updateTile("units",loc,self)
		self.position = loc

	# move in specified direction if tile exists/is empty. expand failures later.
	def move(self,direction):
		dest = dirOffset(self.position,direction)
		if dest[0] >= 0 and dest[1] >= 0 and dest[0] < self.realm.xsize and dest[1] < self.realm.xsize:
			movcost = self.realm.data["ground"][dest[0]][dest[1]].movement
			if movcost <= self.ap:
				if self.realm.data["units"][dest[0]][dest[1]] == None:
					self.changeLoc(dest)
					self.ap -= movcost
					return "moving unit to %s" % dest
				else:
					# space is occupied
					return "error: space occupied"
			else:
				# insufficient action points to continue
				return "error: insufficient AP"
		else:
			#destination out of range
			return "error: bad destination"


	# this ends the units turn
	def endTurn(self):
		self.ap = 0


	# this adds the unit's order to the queue using a predicted ap value
	def takeAction(self):
		direction =- 1
		while direction != 5:
			if self.ai == 1:
				direction = random.randint(0,9)
			else:
				try:
					direction = int(raw_input("Which direction to move %s? " % self.name))
				except ValueError:
					direction = 5
			if direction != 5:
				self.team.addOrder({"unit" : self, "action" : "move", "direction" : direction})
		self.team.addOrder({"unit" : self, "action" : "end"})
		


class Team(object):
	"""These contain lists of units that belong to one side.
	name = the name of the team
	members = the units on the team
	queue = the command queue for the current turn"""
	def __init__(self, name):
		super(Team, self).__init__()
		self.name = name
		self.members = {}
		self.queue = []

	# add/remove units to the list of members
	def addMember(self, unit, name):
		self.members[name] = unit

	def removeMember(self, index):
		del(self.members[index])

	# add an order to the queue
	def addOrder(self, order):
		self.queue.append(order)

	# players give units orders. then the orders are executed.
	def takeTurn(self,ai):
		self.queue = []
		if ai == 0:
			name = None
			while name != "":
				name = str(raw_input("Which unit to move? "))
				try:
					unit = self.members[name]
					unit.ap = unit.maxap
					unit.takeAction()
				except KeyError:
					if name != "":
						print "That unit doesn't exist!"
		else:
			for key, value in self.members.iteritems():
				value.ap = value.maxap
				value.takeAction()

		for order in self.queue:
			if order["action"] == "move":
				order["unit"].move(order["direction"])
			elif order["action"] == "end":
				order["unit"].endTurn()

		
# main
if __name__ == '__main__':
	# create terrain
	grassTile = TerrainType(" ",1,1)
	hillTile = TerrainType("^",1,2)

	# create map
	world = Map(11,11)
	world.generateFlat(grassTile)
	for i in xrange(random.randint(10,35)):
		world.updateTile("ground",[random.randint(0,10),random.randint(0,10)],hillTile)

	# create teams
	teamone = Team("Red")
	for i in xrange(0,4):
		Unit("%d" % i,"human","%d" % i,world,teamone,[i,0],2,0)

	teamtwo = Team("Blu")
	for i in xrange(0,8):
		Unit("Z","zombie","zombie%d" % i,world,teamtwo,[10-i,10],1,1)

	while True:
		# display world
		print
		world.dispMap()
		# advance the turn
		teamone.takeTurn(0)
		teamtwo.takeTurn(1)
		time.sleep(0.2)