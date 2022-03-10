import sys
import requests
import os

summoner_name = "Robert Lucci"
league_version = "12.5.1"

def get_players():
    response = requests.get("https://127.0.0.1:2999/liveclientdata/playerlist", verify = False)
    players = response.json()
    return players

def get_gamemode():
    response = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
    game_info = response.json()
    return game_info["gameMode"]

def get_base_cooldowns():
    ssInfo = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{league_version}/data/en_US/summoner.json")
    summoner_spells = ssInfo.json()['data']
    cooldowns = {summoner_spells[key]['name']: summoner_spells[key]['cooldown'][0] for key in summoner_spells.keys()}
    cooldowns["Challenging Smite"] = 15
    cooldowns["Chilling Smite"] = 15 
    cooldowns["Unleashed Teleport"] = 240
    return cooldowns

def get_sums(playerlist, mode, base_cds):
    for player in playerlist:
        if player['summonerName'] == summoner_name:
            my_team = player['team']

    summoner_table = {}
    for player in playerlist:
        if player['team'] != my_team and player['summonerSpells']: #remember to change this back to enemy team
            ss1 = player['summonerSpells']['summonerSpellOne']['displayName']
            ss2 = player['summonerSpells']['summonerSpellTwo']['displayName']
            #Check game time. If game is past 14 minutes: TP cooldown changes.
            ss1CD = base_cds[ss1]
            ss2CD = base_cds[ss2]
            # if ss1 == "Teleport":
            #     game_time = get_ingame_time()
            #     if game_time >= 14*60:
            #         ss1CD = 240
            # if ss2 == "Teleport":
            #     game_time = get_ingame_time()
            #     if game_time >= 14*60:
            #         ss2CD = 240
            #Take into account summoner spell haste from items/runes/game_mode
            summoner_haste = 0
            #Check if the mode is ARAM, which has extra summoner haste.
            if mode == "ARAM":
                summoner_haste += 70
            #Check if they're running lucidity boots
            for item in player['items']:
                if item['displayName'] == "Ionian Boots of Lucidity":
                    summoner_haste += 12
            #Check if they're running inspiration. If they are, assume that they'll run cosmic insight
            if player['runes']['primaryRuneTree']['displayName'] == "Inspiration" or player['runes']['primaryRuneTree']['displayName'] == "Inspiration":
                summoner_haste += 18
            #Apply summoner spell haste

            ss1CD *= 100/(summoner_haste + 100)
            ss2CD *= 100/(summoner_haste + 100) 

            summoner_table[player['championName']] = [[ss1,ss1CD], [ss2,ss2CD]]
            
    return summoner_table


def get_ingame_time():
    response = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify = False)
    game_stats = response.json()
    ingame_time = game_stats['gameTime']
    return ingame_time


if __name__=="__main__":
    from datetime import timedelta
    players = get_players()
    gamemode = get_gamemode()
    base_cds = get_base_cooldowns()
    champions = get_sums(players, gamemode, base_cds)
    print(f"pulling summoner spell data for champions as of: {timedelta(seconds=get_ingame_time())} \n {champions}")