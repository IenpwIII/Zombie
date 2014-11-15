import random
import time
import json

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
	Realm = which Map the unit is on
	Domain = land/sea/air/etc.
	AP = number of action points allotted to the unit per turn
	Position = where the unit is located on the map
	Action = current action of the unit"""
	def __init__(self, icon, realm, team, position, ap, action):
		super(Unit, self).__init__()
		self.icon = icon
		self.realm = realm
		self.team = team
		self.position = position
		self.maxap = ap
		self.action = action
		# add the unit to its team
		self.team.addMember(self)
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


	# this will be updated to contain the action/pathfinding logic or something. For now it just moves the unit like a derp
	def takeAction(self):
		self.ap = self.maxap
		while self.ap > 0:
			direction = random.randint(0,9)
			if direction != 5:
				self.move(direction)
			else:
				#skip turn
				self.ap = 0
		


class Team(object):
	"""These contain lists of units that belong to one side."""
	def __init__(self, name):
		super(Team, self).__init__()
		self.name = name
		self.members = []

	# add/remove units to the list of members
	def addMember(self, member):
		self.members.append(member)

	def removeMember(self, index):
		del(self.members[index])

	# each unit takes its action when the turn is advanced
	def takeTurn(self):
		for i in self.members:
			i.takeAction()


		
# main
if __name__ == '__main__':
	# create terrain
	grassTile = TerrainType("-",1,1)
	hillTile = TerrainType("^",1,2)

	# create map
	world = Map(11,11)
	world.generateFlat(grassTile)
	for i in xrange(random.randint(0,121)):
		world.updateTile("ground",[random.randint(0,10),random.randint(0,10)],hillTile)

	# create teams
	teamone = Team("Red")
	zoms = []
	for i in xrange(0,4):
		zoms.append(Unit("%s" % i,world,teamone,[i,0],1,0))

	while True:
		# display world
		print
		world.dispMap()
		# advance the turn
		teamone.takeTurn()
		time.sleep(0.2)