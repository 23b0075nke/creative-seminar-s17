#Encapsulates three objects used in Shrine: gamestate, offerings, and storyevents
#	classes used as management tools for tracking and editing different elements of the system (state variables, assets displayed onscreen, etc)
from kivy.properties import NumericProperty
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher
from kivy.core.audio import SoundLoader 
from kivy.uix.image import Image


#GameState: Three state variables for the story
class GameState:

	#Declared as class attr, common to all instances of the class
	community = 0
	environment = 0 
	outsiders = 0 
	current_total = 0
	prev_total = 0

	#Possibly need to make these class attr as well? 
	#Or not, because all classes are mutably accessing the same instances of these objects (scary?)
	def __init__(self, bglayout, relationshipmask, offeringslayout, storylayout):
		self.bglayout = bglayout
		self.offeringslayout = offeringslayout
		self.storylayout = storylayout
		self.relationshipmask = relationshipmask

	#Print state variables for debugging
	def print_state(self):
		state = "\tCurrent gamestate: " + "\n"
		state = state + "\tTotal effects: " + str(GameState.current_total) + "\n"
		state = state + "\tEnvironment: " + str(GameState.environment)  + "\n"
		state = state + "\tCommunity: " + str(GameState.community) + "\n"
		print state + "\tOutsiders: " + str(GameState.outsiders) + "\n"

	#Edit state variables (add positive or negative results)
	def update_env(self, n):
		GameState.environment = GameState.environment + n
		return GameState.environment

	def update_com(self, n):
		GameState.community = GameState.community + n
		return GameState.community

	def update_out(self, n):
		GameState.outsiders = GameState.outsiders + n
		return GameState.outsiders

	def update(self, e, c, o):
		#print 'updating gamestate. current total/prev total ', GameState.current_total, GameState.prev_total
		GameState.prev_total = GameState.current_total
		GameState.environment = GameState.environment + e
		GameState.community = GameState.community + c
		GameState.outsiders = GameState.outsiders + o
		GameState.current_total = GameState.environment + GameState.community + GameState.outsiders

	def reset(self, event):
		print "resetting gamestate"
		GameState.community = 0
		GameState.environment = 0 
		GameState.outsiders = 0 
		GameState.current_total = 0 
		GameState.prev_total = 0
		self.offeringslayout.reset()
		self.relationshipmask.reset()
		self.storylayout.reset(self)

#Offering: An object placed at the shrine by a villager. 
#Collection of variables for access - image, sound, location of placement
class Offering(Image):
	def __init__(self, oid, imageloc, soundloc, sound, minx, miny, maxx, maxy, **kwargs):
		super(Offering, self).__init__(**kwargs)
		self.oid = oid
		self.source = imageloc
		self.sfx_src = soundloc
		self.sound = sound
		self.xmin = minx
		self.ymin = miny
		self.xmax = maxx
		self.ymax = maxy

	def print_offering(self):
		print "		Offering: " + str(self.oid)
		print "			Img:" + self.img_src
		print "			Sfx:" + self.sfx_src
		print "			xrange: (" + str(self.xmin) + ", " + str(self.xmax) + ")"
		print "			yrange: (" + str(self.ymin) + ", " + str(self.ymax) + ")"

	def play_sound(self):
		if self.sound:
			#print("Sound found at %s" % self.sound.source)
			self.sound.loop = True
			self.sound.play()
		else:
			print 'Problem loading sound on offering ', self.oid

	def stop_sound(self):
		if self.sound:
			#print("Sound found at %s" % self.sound.source)
			self.sound.stop()
		else:
			print 'Problem loading sound on offering ', self.oid

#Storyevent: A question posed by the villager, with given prerequisites, responses, and choice effects
#	Prerequisites listed [environment, community, outsiders]
#	Responses a tuple with (response text, [E,C,O] results)
#	Each event assigned an offering left behind (placed onscreen) when user selects a response. 
class StoryEvent:
	def __init__(self, qid, prereq, question, responses, offering):
		self.qid = qid 
		self.prerequisites = prereq
		self.question = question
		self.responses = responses
		self.offering = offering

	def print_event(self):
		print "Story event: " + str(self.qid)
		print self.question
		print self.prerequisites
		print self.response1
		print self.response2
		print self.response3
		self.offering.print_offering()