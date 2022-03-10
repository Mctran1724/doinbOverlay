# doinbOverlay

An overlay for League of Legends to facilitate developing the habit of timing important summoner spell cooldowns on the enemy team. Currently, typing summoner spells manually can be cumbersome and difficult. The goal is to make that easier. This project is in a developmental phase. Many possible features have yet to be added. Currently, it is in it's first functional form. This is meant as a quick foray into app development for me. Advice is welcome.

Note: you must be logged in and in a current game to access the Riot Games live game API.
Overlay requires windowed mode in-game.
my_summoner_name is hardcoded for now.


Potential additions: 
 - Being able to toggle the overlay with a hotkey. 
 - Type summoner spells on hotkey instead of button click. 
 - Include Ultimate Cooldowns. 


Updates: 
 - Added new button for updating CDs when enemies purchase Ionian Boots of Lucidity/Teleport unleashes.
 - Added window close button. 
 - Split functionality between two scripts.

Usage:
 - Start a game of League of Legends. 
 - Run build_window.py
 - When summoner spells are used, enqueue them by clicking the appropriate button
 - When ready to time the summoner spells in chat, click the button or use the "ctrl+t" hotkey.
 - If the opponents buy Ionian Boots of Lucidity or they have teleports that unleash, update the timers with the bottom button. 
 - Close the app with the button in the top right when done. 

doinbOverlay isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
