"""
http://www.reddit.com/r/dailyprogrammer/comments/27h53e/662014_challenge_165_hard_simulated_ecology_the/
"""

import random
from math import floor

class Simulation():
	def __init__(self, edge):
		self.month = 0
		self.map = Map(self, edge)
		self.annualGraphs = []

	def date(self):
		return self.month // 12, self.month % 12 #year, month
		
	def dates(self):
		year, month = self.date()
		month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month]
		
		return "{} {:04}".format(month, year)

	def simulate(self, years):
		map = self.map
		
		self.annual()
		
		while self.month < years * 12:
			Tree.monthlySaplings     = 0
			Lumberjack.monthlyLumber = 0
			Bear.monthlyMaulings     = 0
			
			self.month += 1
			map.tick()
			
			# monthly log
			if Lumberjack.monthlyLumber > 0: 
				print("{}: {} pieces of lumber harvested".format(self.dates(), Lumberjack.monthlyLumber))
			if Tree.monthlySaplings > 0:     
				print("{}: {} new saplings sprouted".format(self.dates(), Tree.monthlySaplings))
			if Bear.monthlyMaulings > 0:
				print("{}: {} lumberjacks mauled by bears".format(self.dates(), Bear.monthlyMaulings))
			
			if map.count(Tree) == 0: # trees are gone; simulation ends
				self.annual()
				break
			
			if self.month % 12 == 0:
				self.annual()
		
		print("\n".join(self.annualGraphs)) #last line gets emitted twice

	def annual(self):
		year, month = self.date()
		map = self.map
		
		#update lumberjacks based on productivity
		ljs = [l for l in map.objects if type(l) is Lumberjack]
		productivity = Lumberjack.annualLumber / len(ljs)
		if productivity < 1 and len(ljs) > 1: 
			random.choice(ljs).remove()
			dljp = -1 # delta lumberjack population
		else: 
			dljp = floor(productivity)
			for i in range(dljp):
				#spawn a new lumberjack at random
				x = random.randint(0, map.edge - 1)
				y = random.randint(0, map.edge - 1)
				map.objects.append(Lumberjack(map, x, y))
		Lumberjack.annualLumber = 0
		
		#update bears based on maulings
		if Bear.annualMaulings == 0:
			dbp = 1 #delta bear population
			x = random.randint(0, map.edge - 1)
			y = random.randint(0, map.edge - 1)
			map.objects.append(Bear(map, x, y))
		else:
			dbp = -Bear.annualMaulings
			for i in range(Bear.annualMaulings):
				if map.count(Bear) == 0:
					break
				map.choice(Bear).remove()
		maulings = Bear.annualMaulings
		Bear.annualMaulings = 0
		
		#census
		saplings = 0
		trees = 0
		elders = 0
		ljs = 0
		bears = 0
		for o in map.objects:
			if type(o) is Tree:
				if o.type() == 'sapling': saplings += 1
				if o.type() == 'tree':    trees    += 1
				if o.type() == 'elder':   elders   += 1
			if type(o) is Lumberjack:     ljs      += 1
			if type(o) is Bear:           bears    += 1
		
		area = map.edge ** 2
		ag = "{:04}: [".format(year)
		ag += 'B' * (50 * bears // area)
		ag += 'T' * (50 * map.count(Tree) // area)
		ag += 'L' * (50 * ljs // area)
		ag += '_' * (50 - sum((50 * bears // area, 50 * map.count(Tree) // area, 50 * ljs // area)))
		ag += ']'
		self.annualGraphs.append(ag)
		
		
		# emit annual log
		print()
		print("{:04}: Forest has {} saplings, {} trees, {} elder trees, {} lumberjacks and {} bears"
			  .format(year, saplings, trees, elders, ljs, bears))
		if maulings > 0:
			print("{:04}: For {} maulings this year {} bear killed".format(year, maulings, -dbp))
		else:
			print("{:04}: 1 bear cub matures".format(year))
		if productivity < 1:
			if dljp < 0:
				print("{:04}: Given low productivity of {:.1f} lumber per jack, 1 was fired"
					  .format(year, float(productivity)))
			else:
				print("{:04}: The lone lumberjack harvested no trees this year".format(year))
		else:
			print("{:04}: Given productivity of {:.1f} lumber per jack, {} were hired"
				  .format(year, float(productivity), dljp))
		print()
	
class Map():
	def __init__(self, simulation, edge=10):
		self.sim = simulation
		self.edge = edge
		self.map = [[[] for e in range(edge)] for f in range(edge)] # [x][y][objects]
		self.objects = [] # list of objects on the map
		
		for x, y, o in self.locations():
			if random.random() < .1: # 10% spawn rate
				self.objects.append(Lumberjack(self, x, y))
			if random.random() < .5:
				#how old should this random tree be?
				age = 100 // (random.randint(1, 10) ** 2) #years; a nice distribution of old and new
				age *= 12 # convert years to months
				age -= random.randint(0, 11) # divide within the years
				self.objects.append(Tree(self, x, y, age))
			if random.random() < .02:
				self.objects.append(Bear(self, x, y))
		
	def tick(self):
		for object in self.objects:
			object.tick()

	def count(self, Type):
		return sum((1 if type(o) is Type else 0 for o in self.objects))
			
	def locations(self):
		"""
		For every location in the map, yield the coordinates and the list of objects present at that location
		"""
		for x in range(self.edge):
			for y in range(self.edge):
				yield x, y, self.map[x][y]
	
	def choice(self, Type):
		"Return a random population member of given Type"
		return random.choice([o for o in self.objects if type(o) is Type])
				
class MapObject():
	def __init__(self, map, x, y):
		"""
		Create a new object on the map.
		"""
		self.map = map
		self.x = x
		self.y = y
		
		self.colocated().append(self) #place self into the locations grid
		
	def adjacent(self):
		"""
		Iterate over all squares adjacent to the current location.
		
		Return absolute locations on the map.
		"""
		
		for x in [-1, 0, 1]:
			if x + self.x < 0 or x + self.x > self.map.edge - 1:
				continue
				
			for y in [-1, 0, 1]:
				if y + self.y < 0 or y + self.y > self.map.edge - 1:
					continue
				
				if not (x == 0 and y == 0):
					yield x + self.x, y + self.y
				
	def colocated(self, x=None, y=None):
		"Return a list of all objects in the same grid square"
		if x is None or y is None: x, y = self.x, self.y
		return self.map.map[x][y]
		
	def remove(self):
		"Remove this object from the map"
		self.colocated().remove(self)
		self.map.objects.remove(self)
		
class MobileObject(MapObject):
	def wander(self):
		self.colocated().remove(self)
		self.x, self.y = random.choice(list(self.adjacent()))
		self.colocated().append(self)
		
		return self.seek()
		
class Tree(MapObject):
	monthlySaplings = 0

	def __init__(self, map, x, y, age=0):
		super().__init__(map, x, y)
		self.born = self.map.sim.month - age
		
	def age(self):
		return self.map.sim.month - self.born
		
	def type(self):
		if self.age() < 12:  return "sapling"
		if self.age() >= 120: return "elder"
		return "tree"
		
	def tick(self):
		spawn = False # sapling case
		if self.type() == 'tree':
			# business logic: 10% chance of spawn in empty adjacent
			spawn = random.random() < .1
		elif self.type() == 'elder':
			# business logic: 20% chance of spawn in empty adjacent
			spawn = random.random() < .2
		if spawn:
			openAdj = [(x, y) for x, y in self.adjacent() if len(self.colocated(x, y)) == 0]
			if len(openAdj) > 0:	
				Tree.monthlySaplings += 1
				x, y = random.choice(openAdj)
				self.map.objects.append(Tree(self.map, x, y))
				
class Lumberjack(MobileObject):
	monthlyLumber = 0
	annualLumber = 0

	def seek(self):
		"True if found a non-sapling tree or bear"
		for o in self.colocated():
			if type(o) is Tree:
				if o.type != 'sapling':
					return True
			if type(o) is Bear:
				return True
		return False
		
	def tick(self):
		for i in range(3):
			if self.wander(): break
		
		#check for found a bear
		if len([b for b in self.colocated() if type(b) is Bear]) > 0:
			Bear.maul(self)
		
		#check for found lumber
		trees = [o for o in self.colocated() if type(o) is Tree]
		for t in trees:
			if t.type() == 'tree':    
				Lumberjack.monthlyLumber += 1
				Lumberjack.annualLumber  += 1
			if t.type() == 'elder':   
				Lumberjack.monthlyLumber += 2
				Lumberjack.annualLumber  += 2
			if t.type() != 'sapling': t.remove()
			
class Bear(MobileObject):
	monthlyMaulings = 0
	annualMaulings = 0

	def seek(self):
		"True if found a lumberjack"
		for o in self.colocated():
			if type(o) is Lumberjack:
				return True
		return False
		
	def tick(self):
		for i in range(5):
			if self.wander(): break
		
		for o in self.colocated():
			if type(o) is Lumberjack: 
				Bear.maul(o)
	
	@classmethod
	def maul(cls, lj):
		cls.monthlyMaulings += 1
		cls.annualMaulings  += 1
		lj.remove()
		if lj.map.count(Lumberjack) == 0:
			#spawn new lumberjack
			x = random.randint(0, lj.map.edge - 1)
			y = random.randint(0, lj.map.edge - 1)
			lj.map.objects.append(Lumberjack(lj.map, x, y))
		
		
if __name__ == '__main__':
	import argparse
	
	parser = argparse.ArgumentParser(description='Simulate a forest ecology with lumberjacks and bears.')
	parser.add_argument('-e', '--edge', default=10, type=int, 
	                    help='Edge length of the (square) forest simulated')
	parser.add_argument('-y', '--years', default=400, type=int,
	                    help='How long in years to simulate')
						
	args = parser.parse_args()
	
	Simulation(args.edge).simulate(args.years)
	
