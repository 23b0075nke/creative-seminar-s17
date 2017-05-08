
#Imports --------------------
import xlrd
import kivy
import gameparsers
import gameobjects
import gamewidgets
from kivy.app import App
import kivy.app
from kivy.config import Config
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.label import Label


#Load kv file --------------------
from kivy.lang import Builder
Builder.load_file('shrine.kv')

#Set config stuff -----------------
#Config.set('graphics', 'fullscreen', 'auto')
#Window.fullscreen = 'auto'
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

#Main Game Loop --------------------
#Entry point for the game loop. Initializes layout widgets.
class GameApp(App):
	def build(self):
		background = gamewidgets.start_game()
		return background
#Run 
if __name__ == '__main__':
	GameApp().run()