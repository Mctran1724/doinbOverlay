from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog
from PyQt5 import QtGui, QtCore

import keyboard
import requests
import time
import sys
from datetime import timedelta

my_summoner_name = "403N"

class Overlay(QWidget):
	def __init__(self, champions):
		super().__init__()
		self.champions = champions
		self.setGeometry(1200,200,150,300)
		self.setWindowOpacity(0.75) #Natural opacity
		visible = True
		self.sstimers = []

		#Make the window stay on top so it's an overlay, and remove the border
		self.setWindowFlags(
			QtCore.Qt.WindowStaysOnTopHint |
			QtCore.Qt.FramelessWindowHint 
			)

		vboxMain = QVBoxLayout()
		timertypeButton = QPushButton("Type Timers", self)
		timertypeButton.clicked.connect(self.typeTimers)
		vboxMain.addWidget(timertypeButton)


		for x in champions:
			vboxMain.addWidget(self.addChampion(x))


		self.setLayout(vboxMain)
		self.show()



	def addChampion(self, champion):
		box = QGroupBox(champion)
		layout = QHBoxLayout()

		ss1 = QPushButton(self.champions[champion][0][0], self)
		ss2 = QPushButton(self.champions[champion][1][0], self)

		ss1.clicked.connect(lambda: self.addTimer(champion, 0))
		ss2.clicked.connect(lambda: self.addTimer(champion, 1))

		layout.addWidget(ss1)
		layout.addWidget(ss2)

		box.setLayout(layout)
		return box

	
	def addTimer(self, champion, ss): #ss1 or ss2
		response = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
		gameStats = response.json()
		gameTime = gameStats['gameTime']
		#Straightforwardly add the cooldown length to the game time for the timer. 

		ssName = self.champions[champion][ss][0]
		ssTime = self.champions[champion][ss][1] + gameTime
		if ssName in ssNicknames:
			self.sstimers.append([champion, ssNicknames[ssName], ssTime])
		else:
			self.sstimers.append([champion, ssName, ssTime])
		self.sstimers = sorted(self.sstimers, key = lambda x: x[-1]) #Sort the timers by when they will end

	

	def typeTimers(self):
		response = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
		gameStats = response.json()
		gameTime = gameStats['gameTime']
		#Remove timers that have passed
		#Remove all the ones where the gameTime is beyond the timer the summoner spell comes back up.
		#Those will always be from the front, since the earliest ending ones are in the front due to sorting.
		while self.sstimers[0][-1] <= gameTime: 
			self.sstimers.pop(0)


		timerText =" ".join([f"{x[0]} {x[1]} {timedelta(seconds = int(x[2]))}" for x in self.sstimers])
		keyboard.send("alt+tab") #Change this to "command+tab" if using mac.
		keyboard.send("enter")
		keyboard.write(timerText)
		keyboard.send("enter")

	def disappearOverlay(self):
		

def getSummonerSpellsInfo():
	ssInfo = requests.get("http://ddragon.leagueoflegends.com/cdn/11.18.1/data/en_US/summoner.json")
	return ssInfo.json()['data']


sums = getSummonerSpellsInfo()
ssCooldowns = {sums[key]['name']: sums[key]['cooldown'][0] for key in sums.keys()}
ssCooldowns['Teleport'] = 420
ssNicknames = {"Flash": 'f', "Teleport": "tp", "Ignite": "Ig", "Exhaust": "Exh"}


def getSums(playerlist):
	for player in playerlist:
		if player['summonerName'] == my_summoner_name:
			my_team = player['team']

	enemy_sums = {}
	for player in playerlist:
		if player['team'] != my_team and player['summonerSpells']:
			ss1 = player['summonerSpells']['summonerSpellOne']['displayName']
			ss2 = player['summonerSpells']['summonerSpellTwo']['displayName']

			#Take into account that teleport's cooldown changes with level
			if ss1 == "Teleport":
				ss1CD = 420 - 210 / 17 * (player['level'] - 1)
				ss2CD = ssCooldowns[ss2]
			elif ss2 == "Teleport":
				ss1CD = ssCooldowns[ss1]
				ss2CD = 420 - 210 / 17 * (player['level'] - 1)
			else:
				ss1CD = ssCooldowns[ss1]
				ss2CD = ssCooldowns[ss2]

			#Take into account summoner spell haste from items/runes
			summonerSpellHaste = 0
			#Check if they're running lucidity boots
			for item in player['items']:
				if item['displayName'] == "Ionian Boots of Lucidity":
					summonerSpellHaste += 12
			#Check if they're running inspiration. If they are, assume that they'll run cosmic insight
			if player['runes']['primaryRuneTree']['displayName'] == "Inspiration" or player['runes']['primaryRuneTree']['displayName'] == "Inspiration":
				summonerSpellHaste += 18
			#Apply summoner spell haste

			ss1CD *= 100/(summonerSpellHaste + 100)
			ss2CD *= 100/(summonerSpellHaste + 100) 

			enemy_sums[player['championName']] = [[ss1,ss1CD], [ss2,ss2CD]]

	return enemy_sums


def accessGame():
	response = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify = False)
	playersInfo = response.json()
	enemy_sums = getSums(playersInfo)

	return enemy_sums


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Overlay(accessGame())
	sys.exit(app.exec())

