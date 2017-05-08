#Encapuslates parsing functions for creating offerings and story events from excel "lookup table"
# 	uses xlrd module to pull data into memory 
#	sheets used for easy organization of information for parsing, ease of editability
#	offerings and storyevents manage data used to display and calculate the effects of offerings, story events, user responses, etc. (see: gameobjects.py)

import xlrd 
import gameobjects
import random
from kivy.core.audio import SoundLoader 

eventsheet = xlrd.open_workbook('../GameObjects.xls').sheet_by_index(0)
offeringsheet = xlrd.open_workbook('../GameObjects.xls').sheet_by_index(1)

'''
NOTES:
	Offerings Spreadsheet organized as follows: 
	A = 0, B = 1, etc. Columns are zero-indexed.
		(0, x) label row
		(x, 0) Offering ID 
		(x, 1) Offering image filepath
		(x, 2-3) Range of x locations for offering
		(x, 4-5) Range of y locations for offering
		(x, 6) Offering sound filepath
'''
#Load sound file into memory
def get_sound(path):
	sound = SoundLoader.load(path)
	if sound:
		sound.loop = True
	return sound

#Create offering object from table data
def create_offering(rowidx):
	oid = int(offeringsheet.cell(rowidx,0).value)
	print "Creating offering: " + str(oid)
	imageloc = str(offeringsheet.cell(rowidx,1).value).strip()
	soundloc = str(offeringsheet.cell(rowidx,6).value).strip()
	sound = get_sound(soundloc)
	minx = int(offeringsheet.cell(rowidx,2).value)
	miny = int(offeringsheet.cell(rowidx,4).value)
	maxx = int(offeringsheet.cell(rowidx,3).value)
	maxy = int(offeringsheet.cell(rowidx,5).value)
	return gameobjects.Offering(oid, imageloc, soundloc, sound, minx, miny, maxx, maxy)

def create_all_offerings():
	offerings = []
	for rowidx in range(1, offeringsheet.nrows-1):
		offerings.append(create_offering(rowidx))
	return offerings

'''
NOTES:
	Events Spreadsheet organized as follows: 
	A = 0, B = 1, etc. Columns are zero-indexed.
		(0, x) label row
		(x, 0) Question ID 
		(x, 1) Question Text
		(x, 2-4) Question Prerequisites
		(x, 5) Response 1 
		(x, 6-8) Response 1 results
		(x, 9) Response 2
		(x,10-12) Response 2 results
		(x, 13) Response 3
		(x,14-16) Response 3 results

	Question stored as string.
	Prereqs stores as list: [environment, community, outsiders] (ECO)
	Responses stored in tuples: text, results
'''

def create_event(rowidx):
	qid = int(eventsheet.cell(rowidx,0).value)
	print "Creating Story Event: " + str(qid)
	question = (str(eventsheet.cell(rowidx,1).value).strip())
	prereqs = [int(eventsheet.cell(rowidx,2).value), int(eventsheet.cell(rowidx,3).value), int(eventsheet.cell(rowidx,4).value)]

	responses = []
	if len(eventsheet.cell(rowidx,5).value.strip()) > 0:
		responses.append((str(eventsheet.cell(rowidx,5).value).strip(), [int(eventsheet.cell(rowidx,6).value), int(eventsheet.cell(rowidx,7).value), int(eventsheet.cell(rowidx,8).value)]))
	if len(str(eventsheet.cell(rowidx,9).value.strip())) > 0:
		responses.append((str(eventsheet.cell(rowidx,9).value).strip(), [int(eventsheet.cell(rowidx,10).value), int(eventsheet.cell(rowidx,11).value), int(eventsheet.cell(rowidx,12).value)]))
	if len(str(eventsheet.cell(rowidx,13).value.strip())) > 0:
		responses.append((str(eventsheet.cell(rowidx,13).value).strip(), [int(eventsheet.cell(rowidx,14).value), int(eventsheet.cell(rowidx,15).value), int(eventsheet.cell(rowidx,16).value)]))

	offering = create_offering(random.randint(1, offeringsheet.nrows-1))
	return gameobjects.StoryEvent(qid, prereqs, question, responses, offering)

def create_all_events():
	storyevents = []
	for rowidx in range(1, eventsheet.nrows):
		storyevents.append(create_event(rowidx))
	return storyevents

