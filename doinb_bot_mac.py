from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5 import QtCore
import keyboard
import requests
import time
import sys
from datetime import timedelta

#Input your summoner name, so we can calculate which are the opponents.
my_summoner_name = "Robert Lucci"

class Overlay(QWidget):
	def __init__(self, champions):
		super().__init__()
		self.champions = champions
		self.setGeometry(1250,150,100,200)
		self.setWindowOpacity(0.75) #Natural opacity
		visible = True
		self.sstimers = []

		#Make the window stay on top so it's an overlay, and remove the border
		self.setWindowFlags(
			QtCore.Qt.WindowStaysOnTopHint |
			QtCore.Qt.FramelessWindowHint 
			)

		#Use a vertical layout to hold each champion
		vboxMain = QVBoxLayout()
		vboxMain.setContentsMargins(0,0,0,0)
		timertypeButton = QPushButton("Type Timers", self)
		timertypeButton.clicked.connect(self.typeTimers)
		vboxMain.addWidget(timertypeButton)

		#Add every champion on the enemy team
		for x in champions:
			vboxMain.addWidget(self.addChampion(x))


		self.setLayout(vboxMain)
		self.show()



	def addChampion(self, champion):
		box = QGroupBox(champion)
		layout = QHBoxLayout()
		layout.setContentsMargins(0,0,0,0)
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
		#alt+tab, then go into chat, then type the timers, then send the chat.
		keyboard.send("command+tab") #For windows/linux, replace "command" with "alt"
		keyboard.send("enter")
		keyboard.write(timerText)
		keyboard.send("enter")



def getSummonerSpellsInfo():
	ssInfo = requests.get("http://ddragon.leagueoflegends.com/cdn/11.18.1/data/en_US/summoner.json")
	return ssInfo.json()['data']


sums = getSummonerSpellsInfo()
ssCooldowns = {sums[key]['name']: sums[key]['cooldown'][0] for key in sums.keys()}
#If you start the program after they've got one of the upgraded smites
ssCooldowns["Challenging Smite"] = 15
ssCooldowns["Chilling Smite"] = 15 
ssCooldowns['Teleport'] = 420


def getSums(playerlist, mode):
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

			#Take into account summoner spell haste from items/runes/game_mode
			summonerSpellHaste = 0
			#Check if the mode is ARAM
			if mode == "ARAM":
				summonerSpellHaste += 70
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
	response = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
	gameInfo = response.json()
	gameMode = gameInfo['gameMode']
	enemy_sums = getSums(playersInfo, gameMode)

	
	return enemy_sums


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Overlay(accessGame())

	sys.exit(app.exec())

