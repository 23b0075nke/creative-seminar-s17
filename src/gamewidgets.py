#Layout widgets and associated helper functions and classes
#Includes game management functions (called by buttons, state transitions)

import xlrd
import kivy
import gameparsers
import gameobjects
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import NumericProperty
import random 
from kivy.core.audio import SoundLoader 

lightval = 0.05 #step to make background brighter/darker
lightinit = 0 #initial brightness value
lightmax = .7 #brightness value that triggers growth endstate

#(Adopted) Hoverbehavior event class, used to animate response buttons (scale up on hover)
"""Hoverable Behaviour (changing when the mouse is on the widget by O. Poyen.
License: LGPL
Author: Oliver POYEN
"""

from kivy.properties import BooleanProperty, ObjectProperty
from kivy.core.window import Window

class HoverBehavior(object):
	"""Hover behavior.

	:Events:
		`on_enter`
			Fired when mouse enter the bbox of the widget.
		`on_leave`
			Fired when the mouse exit the widget 
	"""

	hovered = BooleanProperty(False)
	border_point= ObjectProperty(None)
	'''Contains the last relevant point received by the Hoverable. This can
	be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
	'''

	def __init__(self, **kwargs):
		self.register_event_type('on_enter')
		self.register_event_type('on_leave')
		Window.bind(mouse_pos=self.on_mouse_pos)
		super(HoverBehavior, self).__init__(**kwargs)


	def on_mouse_pos(self, *args):
		pos = args[1]
		inside = self.collide_point(*pos)
		if self.hovered == inside:
			#We have already done what was needed
			return
		self.border_point = pos
		self.hovered = inside
		if inside:
			self.dispatch('on_enter')
		else:
			self.dispatch('on_leave')

	def on_enter(self):
		pass

	def on_leave(self):
		pass

#Custom events/callback function ---------------
#(called after start)
#Widget hierarchy: root -> (Offerings < Story < RelationshipMask)
#	Offerings -> (image/sound widgets for Offering objects onscreen)
#	Story -> (Label, Buttons to display options and text) #could this be generated in the storylayout? where else is it accessed
def start_game():
	#if not restart: 
	background = Background()
	storylayout = StoryLayout()
	offeringslayout = OfferingsLayout()
	relationshipmask = RelationshipMask()

	#Initialize story events & offerings
	gamestate = gameobjects.GameState(background, relationshipmask, offeringslayout, storylayout)

	#Nest widgets:
	background.add_widget(storylayout, 0) #child 2
	background.add_widget(offeringslayout) #child 1
	background.add_widget(relationshipmask) #child 0

	#Add candle animation to bg
	background.add_widget(Image(source='../images/offering_frames/statue_candle2.zip', pos_hint={'center_x': 0.497, 'center_y': 0.849}))
	storylayout.populate_screen(gamestate)

	return background
	
#For use in callback on gamestate update
def update_screen(relationshipmask, offeringslayout, storylayout, gamestate):
	if len(storylayout.storyevents) == 0:
		print "calling storylayout restart"
		if gamestate.relationshipmask.mask_alpha > lightinit:
			storylayout.restart(gamestate)
		else:
			print "calling storylayout end"
			storylayout.end(gamestate)
		'''
		TODO: Fix endstate
		if gamestate.relationshipmask.mask_alpha <= lightinit: #not enough light (end with as much as started)
			storylayout.end(gamestate)
		elif gamestate.relationshipmask.mask_alpha >= lightmax: #enough light (end with arbitrarily enough - set above)
			storylayout.restart(gamestate)
		else: #greater than start, less than needed; quietly loop through again..? 
			gamestate.reset()
		'''

	else: 
		#After a question is asked, update offerings and screen brightness
		#If response results in a net positive, add an offering. Else remove. 
		if gamestate.current_total < gamestate.prev_total:
			#print "Total decreased - removing offering "
			offeringslayout.remove_offering()
			relationshipmask.update_relationship(lightval * -1.0)
		else:
			#print "Total same or incrased - adding offering "
			offeringslayout.add_offering(storylayout.currentevent.offering)
			relationshipmask.update_relationship(lightval)

		#Remove the answered question and display the next
		print "displaying next question"
		print "populating screen from update_screen"
		storylayout.depopulate_screen()
		storylayout.populate_screen(gamestate)

#Layout/UI Widgets ---------------------
class OfferingsLayout(FloatLayout):
	#Arrange offerings in possible screen positions, based on range provided in module
	def add_offering(self, offering):
		offering.play_sound()
		xpos = random.randint(offering.xmin, offering.xmax)
		ypos = offering.ymin
		#print "adding offering at ", xpos, ypos
		offering.pos = (xpos, ypos)
		self.add_widget(offering)

	#Remove a random offering from layout's children
	def remove_offering(self):
		if len(self.children):
			offidx = random.randint(0, (len(self.children)-1))
			offering = self.children[offidx]
			offering.stop_sound()
			self.remove_widget(self.children[offidx])

	def reset(self):
		c = len(self.children) + 1
		for i in range(1, c):
			self.remove_offering()

#Layout widget for dynamic button, text placement 
class StoryLayout(FloatLayout):
	def __init__(self, **kwargs):
		# make sure we aren't overriding any important functionality
		super(StoryLayout, self).__init__(**kwargs)
		self.storyevents = gameparsers.create_all_events()
		self.currentevent = self.storyevents[0]
		random.shuffle(self.storyevents)

	def populate_screen(self, gamestate):
		storyevent = self.get_story_event(gamestate)
		self.currentevent = storyevent
		anim_duration = 5/(1 + gamestate.relationshipmask.mask_alpha)
		#pause_anim = Animation(color=[1,1,1,0], d=anim_duration)
		label_anim = Animation(color=[1,1,1,1], d=anim_duration)
		print storyevent
		#print anim_duration

		#Add event label
		label = StoryLabel(text = self.currentevent.question, pos_hint={'center_x': 0.5, 'center_y': 0.25})
		label.text_size = 1000, 100
		label.halign = 'center'
		self.add_widget(label, 0)
		label_anim.start(label)

		#Dynamically add event response button.
		ctr_posx = .25
		additive = .25
		if len(storyevent.responses) == 3:
			ctr_posx = .25
			additive = .25
		elif len(storyevent.responses) == 2:
			ctr_posx = .33
			additive = .33
		else:
			ctr_posx = .5
			additive = 0

		for response in storyevent.responses:
			button = ResponseButton(response, gamestate)
			button.pos_hint = {'center_x': ctr_posx, 'center_y': 0.15}
			self.add_widget(button, 0)
			ctr_posx += additive
			label_anim.start(button)
		
		#label_anim.start(label)
	def depop_anim_complete(self, animation, widget):
		widget.parent.remove_widget(widget)

	#TODO: nice fade-out (animation)
	def depopulate_screen(self):
		#Fadeout will require restructuring populate_screen class (should call it directly, but doesn't access gamestate)
		#	possibly also pass gamestate to depopulate_screen
		'''
		label_anim = Animation(color=[1,1,1,0], d=1)
		label_anim.bind(on_complete=self.depop_anim_complete)

		for child in self.children:
			label_anim.start(child)
		'''
		self.clear_widgets()

	def end(self, gamestate):
		print "ending game!"
		label_anim = Animation(color=[1,1,1,1], d=3)
		self.depopulate_screen()
		label = StoryLabel(text = "The person kneels and is silent for a long time. Eventually they speak. \n\"Will you crumble? Will you leave us, like the rest?\" ", pos_hint={'center_x': 0.5, 'center_y': 0.25}, halign='center')
		self.add_widget(label)
		button = Button(text= "(Remain silent.)", pos_hint={'center_x': 0.33, 'center_y': 0.15})
		button.bind(on_press=gamestate.reset)
		self.add_widget(button, index=0)
		button1 = Button(text= "No.", pos_hint={'center_x': 0.66, 'center_y': 0.15})
		button1.bind(on_press=gamestate.reset)
		self.add_widget(button1, index=0)
		label_anim.start(button)
		label_anim.start(button1)
		label_anim.start(label)

	def restart(self, gamestate):
		print "restarting game"
		#gamestate.relationshipmask.update_relationship(.3)
		label_anim = Animation(color=[1,1,1,1], d=3)
		self.depopulate_screen()
		label = StoryLabel(text = "The person's face glows in the candlelight. You can just barely read their lips through the brightness and noise. \n \"Thank you\".", pos_hint={'center_x': 0.5, 'center_y': 0.25},halign='center')
		self.add_widget(label)
		button = Button(text= "Thank you.", pos_hint={'center_x': 0.5, 'center_y': 0.15})
		button.bind(on_press=gamestate.reset)
		self.add_widget(button, index=0)
		label_anim.start(button)
		label_anim.start(label)

	def get_story_event(self, gamestate):
		print gamestate.print_state()
		for event in self.storyevents:
			prereqs = event.prerequisites
			if prereqs[0] <= gamestate.environment and prereqs[1] <= gamestate.community and prereqs[2] <= gamestate.outsiders:
				#print "Choosing: " + str(event.qid)
				self.storyevents.remove(event)
				return event
			else:
				print "Skipping " + str(event.qid)
		#If it hits this point, there are no available events
		print "no more available events"
		#self.restart(gamestate)
		print "calling storylayout.end in get_story_event"
		self.end(gamestate)
		#self.storyevents = []
		#gamestate.reset

	def reset(self, gamestate):
		print "resetting storylayout"
		gamestate.print_state
		self.depopulate_screen()
		self.storyevents = gameparsers.create_all_events()
		random.shuffle(self.storyevents)
		self.currentevent = self.storyevents[0]
		#print storyevents
		self.populate_screen(gamestate)

#Overlay brightness widget
class RelationshipMask(FloatLayout):
	#Editable alpha for the image
	mask_alpha = NumericProperty(lightinit)
	
	def __init__(self, **kwargs):
		# make sure we aren't overriding any important functionality
		super(RelationshipMask, self).__init__(**kwargs)

		with self.canvas.before:
			Color(1, 1, 1, self.mask_alpha)  
			self.rect = Rectangle(size=self.size, pos=self.pos)

		self.bind(size=self._update_rect, pos=self._update_rect)


	def update_relationship(self, n):
		self.mask_alpha = self.mask_alpha + n

	def _update_rect(self, instance, value): #is this necessary?
		self.rect.pos = instance.pos
		self.rect.size = instance.size

	def reset(self):
		self.mask_alpha = 0#NumericProperty(lightinit)

#ResponseButton contains custom onclick functionality 
class ResponseButton(Button, HoverBehavior):
	xsize = NumericProperty(.2)
	ysize = NumericProperty(.1)

	def __init__(self, response, gamestate, **kwargs):
		super(ResponseButton, self).__init__(**kwargs)
		self.text = response[0]
		self.results = response[1]
		self.gamestate = gamestate
		self.tsize = self.text_size
		self.bind(on_press=ResponseButton.response_select)
		self.a = Animation(size_hint = (1,1))
	
	def response_select(self):
		self.gamestate.update(self.results[0], self.results[1], self.results[2])
		print "from response_select, storylayout size", len(self.gamestate.storylayout.storyevents)
		update_screen(self.gamestate.relationshipmask, self.gamestate.offeringslayout, self.gamestate.storylayout, self.gamestate) #hacky - should update as a callback on gamestate updating but...

	def on_enter(self, *args):
		animation = Animation(x=500, y=500, font_size=25, d=0.5, t='in_out_quad');
		animation.start(self)

	def on_leave(self, *args): 
		animation = Animation(font_size=20, d=0.5, t='in_out_quad');
		animation.start(self)

#Separate label class to specify different default font in kivy
#	...because text markup interferes with animation for some reason? (TODO: look into implementation)
class StoryLabel(Label):
	def __init__(self, **kwargs):
		super(StoryLabel, self).__init__(**kwargs)

class Background(FloatLayout):
	pass

