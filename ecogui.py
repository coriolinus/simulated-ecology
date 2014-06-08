"""
GUI interface to display ongoing state of eco.py
"""

import pdb
import tkinter as tk
from time import sleep
from eco import *


sapling = '\u237F' # vertical line with middle dot
tree = '\u25B3'    # white up-pointing triangle
elder = '\u25EC'   # white up-pointing triangle with dot

bear = '\u25CF'    # black circle
lumberjack = '\u238A'      # circled triangle down

class GUI(tk.Frame):
	def __init__(self, master=None, edge=10, duration=400):
		self.sim = Simulation(edge)
		self.edge = edge
		self.duration = duration
		self.playing = None
		self.sim.annual()
		
		tk.Frame.__init__(self, master)
		self.pack()
		self.createWidgets()
		
		self.redraw()
		
	def createWidgets(self):
		self.topRow = tk.Frame(self)
		self.topRow['relief'] = 'flat'
		self.topRow.pack(side='top')
		
		self.resetB = tk.Button(self.topRow)
		self.resetB['text'] = '\u2940' # anticlockwise closed circle arrow
		self.resetB['command'] = self.reset
		self.resetB['font'] = ('Helvetica', 20)
		self.resetB.pack(side='left')
		
		self.stepB = tk.Button(self.topRow)
		self.stepB['text'] = '\u25B6' # black right-pointing triangle
		self.stepB['command'] = self.step
		self.stepB['font'] = ('Helvetica', 20)
		self.stepB.pack(side='left')
		
		self.playB = tk.Button(self.topRow)
		self.playB['text'] = '\u27A0' # heavy dashed triangle-headed rightwards arrow
		self.playB['command'] = self.play
		self.playB['font'] = ('Helvetica', 20)
		self.playB.pack(side='left')
		
		# self.stopB = tk.Button(self.topRow)
		# self.stopB['text'] = '\u25FC' # black medium square
		# self.stopB['command'] = self.stop
		# self.stopB['font'] = ('Helvetica', 25)
		# self.stopB.pack(side='left')
		
		self.delayE = tk.Entry(self.topRow)
		self.delay = tk.StringVar()
		self.delayE['textvariable'] = self.delay
		self.delay.set('250')
		self.delayE.pack(side='left')
		
		self.delayLabel = tk.Label(self.topRow, text="ms")
		self.delayLabel.pack(side='left')
		
		self.caption = tk.Label(self)
		for sym in ['sapling', 'tree', 'elder', 'bear', 'lumberjack']:
			self.caption['text'] += "{} = {}\n".format(globals()[sym], sym)
		self.caption['font'] = ('Helvetica', 15)
		self.caption['justify'] = tk.LEFT
		self.caption.pack(side='top')
		
		self.mainDisplay = tk.Frame(self)
		self.mainDisplay['relief'] = 'raised'
		self.mainDisplay['borderwidth'] = 1
		self.mainDisplay['padx'] = 5
		self.mainDisplay['pady'] = 5
		self.mainDisplay.pack(side='top')
		
		#set up display cells
		self.cells = []
		for y in range(self.edge):
			# anonymous row frame
			row = tk.Frame(self.mainDisplay)
			row.pack(side='top')
			# list init
			self.cells.append([])
			
			for x in range(self.edge):
				# anonymous frame for sizing; from http://stackoverflow.com/questions/16363292/label-width-in-tkinter
				f = tk.Frame(row, height=25, width=25)
				f.pack_propagate(0) # don't shrink
				f.pack(side='left')
				
				self.cells[-1].append(tk.Label(f))
				self.cells[-1][-1]['text'] = '*' #debug
				self.cells[-1][-1]['font'] = ('Helvetica', 15)
				self.cells[-1][-1].pack(fill=tk.BOTH, expand=1)
		# fill the text with self.cells[x][y]['text'] = '0'
		
	def redraw(self):
		for x in range(self.edge):
			for y in range(self.edge):
				#display priority, high to low: lumberjack, elder, tree, sapling, bear, blank
				os = self.sim.map.map[x][y]
				if len(os) == 0:
					self.cells[x][y]['text'] = ''
				else:
					types = [type(o) for o in os]
					if Lumberjack in types:
						self.cells[x][y]['text'] = lumberjack
					elif Tree in types:
						trees = sorted([(t.age(), t) for t in os if type(t) is Tree]) #last is oldest tree
						self.cells[x][y]['text'] = globals()[trees[-1][1].type()]
					elif Bear in types:
						self.cells[x][y]['text'] = bear
					else:
						# should never happen
						self.cells[x][y]['text'] = '?'
						
		
	def step(self):
		if self.checkdone():
			if self.sim.month % 12 == 11: #next month will be january, so let's print the annual report
				self.sim.annual()
			self.sim.tick()
			self.redraw()
	
	def play(self):
		# toggle the button
		self.playB['text'] = '\u25FC' # black medium square
		self.playB['command'] = self.stop
		self.delayE.config(state=tk.DISABLED)
		
		# actually play the scene
		self.step()
		delay = int(self.delay.get())
		self.playing = self.after(delay, self.autostep, delay)
		
	def stop(self):
		# toggle the button
		self.playB['text'] = '\u27A0' # heavy dashed triangle-headed rightwards arrow
		self.playB['command'] = self.play
		self.delayE.config(state=tk.NORMAL)
		
		# stop the scene
		try:
			self.after_cancel(self.playing)
		except:
			pass
		self.playing = None
		
	def autostep(self, delay):
		if self.playing is not None:
			if self.checkdone():
				self.step()
				self.playing = self.after(delay, self.autostep, delay)
	
	def checkdone(self):
		"Return True if you should continue; False if you should stop"
		if self.sim.month >= self.duration * 12 or self.sim.map.count(Tree) == 0:
			# pdb.set_trace()
			self.stop()
			self.sim.annual()
			print("\n".join(self.sim.annualGraphs))
			
			# set things up to "reset" configuration
			self.stepB.config(state=tk.DISABLED)
			self.playB.config(state=tk.DISABLED)
			return False
		return True

	
	def reset(self):
		# set the buttons
		self.stepB.config(state=tk.NORMAL)
		self.playB.config(state=tk.NORMAL)

		# reset the simulation
		self.sim = Simulation(self.edge)
		# TODO: clear the output buffer
		self.sim.annual()
		self.redraw()
		
		
if __name__ == '__main__':
	import argparse
	
	parser = argparse.ArgumentParser(description='Simulate a forest ecology with lumberjacks and bears.')
	parser.add_argument('-e', '--edge', default=10, type=int, 
	                    help='Edge length of the (square) forest simulated')
	parser.add_argument('-y', '--years', default=400, type=int,
	                    help='How long in years to simulate')
						
	args = parser.parse_args()
	
	#Simulation(args.edge).simulate(args.years)
	
	root = tk.Tk()
	root.wm_title("Forests, Woodsmen, & Bears, oh my!")
	app = GUI(master=root, edge=args.edge, duration=args.years)
	app.mainloop()
