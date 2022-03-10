import requests
import time
import sys
from datetime import timedelta
import warnings
import access_LOL as access

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QDesktopWidget
from PyQt5 import QtCore
from pynput.keyboard import Key, Controller
import keyboard

warnings.filterwarnings("ignore")



champions_dev = {
                "Malzahar": [["Flash", 300], ["Teleport", 240]],
                "Ashe": [["Flash", 300], ["Heal", 240]],
                "Braum": [["Flash", 300], ["Exhaust", 180]]
            }

class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        try:
            self.players = access.get_players()
            self.gamemode = access.get_gamemode()
            self.base_cds = access.get_base_cooldowns()
            self.champions = access.get_sums(self.players, self.gamemode, self.base_cds)
            print(f"pulling summoner spell data for champions as of: {timedelta(seconds=access.get_ingame_time())} \n {self.champions}")
        except:
            self.champions = champions_dev
            print(f"Using dev sample: \n {self.champions}")
        self.setGeometry(1250,150,200,200)
        self.setWindowOpacity(0.75) #Natural opacity
        visible = True
        self.ss_timers = set()

        #Make the window stay on top so it's an overlay, and remove the border
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint 
            )

        
        self.build_buttons()
        self.move_overlay()
        
        self.show()
        self.pynput_controller = Controller()
        keyboard.add_hotkey("ctrl+t", self.type)

    def build_buttons(self):
        
        #Use a vertical layout to hold all the other buttons 
        vboxMain = QVBoxLayout()
        vboxMain.setContentsMargins(0,0,0,0)

        #Top Hbox layout for timer typing and close button
        top_box = QHBoxLayout()

        #Build exit button
        exit_button = QPushButton("X", self)
        exit_button.adjustSize()
        exit_button.setMaximumSize(exit_button.minimumSizeHint())
        exit_button.clicked.connect(self.exit_app)
        
        #Add timer typing button
        type_timers_button = QPushButton("Type Timers", self)
        type_timers_button.clicked.connect(self.type_timers)
        

        top_box.addWidget(type_timers_button)
        top_box.addWidget(exit_button)
        vboxMain.addLayout(top_box)

        #Add horizontal box for every champion
        for champion in self.champions:
            vboxMain.addWidget(self.add_champion(champion))

        #Add button to update summoner spells if they build summoner haste or change with summoner spellbook
        update_summoners = QPushButton("Update Summoners", self)
        update_summoners.clicked.connect(self.update_summoner_spells)
        vboxMain.addWidget(update_summoners)
        self.setLayout(vboxMain)


    def add_champion(self, champion):
        box = QGroupBox(champion)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        ss1 = QPushButton(self.champions[champion][0][0], self)
        ss2 = QPushButton(self.champions[champion][1][0], self)

        ss1.clicked.connect(lambda: self.add_timer(champion, 0))
        ss2.clicked.connect(lambda: self.add_timer(champion, 1))

        layout.addWidget(ss1)
        layout.addWidget(ss2)

        box.setLayout(layout)
        return box
    
    def type_timers(self):
        timers = self.time_summoners()
        keyboard.send("alt+tab")
        time.sleep(0.2) #may not be necessary depending on your machine because the python executes on a different thread than league...
        keyboard.send("enter") #open league chat
        time.sleep(0.1)
        self.pynput_controller.type(timers)
        #time.sleep(0.25)
        keyboard.send("enter") #send chat
        

    def add_timer(self, champion, spell_index):
        spell = self.champions[champion][spell_index][0]
        cooldown = self.champions[champion][spell_index][1]

        try:
            game_time = access.get_ingame_time()
        except:
            game_time = 100

        timer = cooldown + game_time
        self.ss_timers.add((champion, spell, timer))


    def time_summoners(self):
        #Calculate these by calling the actual info from league client.

        try:
            game_time = access.get_ingame_time()
        except:
            game_time = 360 #sample for testing
        
        #Remove all summoner spells that already have come back up
        for timer in list(self.ss_timers):
            if timer[-1] <= game_time:
                self.ss_timers.remove(timer)
        timer_text =" ".join([f"{x[0]} {x[1]} {timedelta(seconds = int(x[2]))} " for x in self.ss_timers])
        return timer_text

    def move_overlay(self):
        screen = QDesktopWidget().screenGeometry()
        geo = self.geometry()
        x = screen.width() - geo.width()
        y = screen.height()//2 - geo.height() #floor divide to avoid unexpected type
        self.move(x,y)

    def exit_app(self):
        self.close()

    def update_summoner_spells(self):
        self.players = access.get_players()
        self.gamemode = access.get_gamemode()
        self.base_cds = access.get_base_cooldowns()
        self.champions = access.get_sums(self.players, self.gamemode, self.base_cds)
        print(f"pulling summoner spell data for champions as of: {timedelta(seconds=access.get_ingame_time())} \n {self.champions}")


    def type(self):
        timers = self.time_summoners()
        keyboard.send("enter")
        time.sleep(0.15)
        self.pynput_controller.type(timers)
        time.sleep(0.15)
        keyboard.send("enter")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Overlay()
    sys.exit(app.exec())

