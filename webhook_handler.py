import json
import csv

#BGG API - https://github.com/lcosmin/boardgamegeek  /  https://lcosmin.github.io/boardgamegeek/
from boardgamegeek import BGGClient
bgg = BGGClient()

"""
Returns a dict with the min and max age that games should be filtered on
Dict format: 3 fields
    - question: the question being answered [age]
    - min: minimum age to use in filter
    - max: maximum age to use in filter
"""
def player_age_response(text):
    d = {"question" : "age"}
    if text == 'Toddler (2-5 years old)':
        d['min'] = 2
        d['max'] = 5
    elif text == 'Children (6-11 years old)':
        d['min'] = 6
        d['max'] = 11
    elif text == 'Youth (12-16 years old)':
        d['min'] = 10
        d['max'] = 16
    elif text == 'Adult (17+ years old)':
        d['min'] = 12
        d['max'] = 100
    else:
        d['min'] = 2
        d['max'] = 100
    return d
    
"""
Returns a dict with the min and max players that games should be filtered on
Dict format: 3 fields
    - question: the question being answered [num_players]
    - min: minimum number of players to use in filter
    - max: maximum number of players to use in filter
"""
def player_num_response(text):
    d = {"question" : "num_players"}
    if text == 'Solo or Pair (1-2 players)':
        d['min'] = 1
        d['max'] = 2
    elif text == 'Small Group (2-4 players)':
        d['min'] = 2
        d['max'] = 4
    elif text == 'Party (5+ players)':
        d['min'] = 5
        d['max'] = 100  
    else:
        d['min'] = 1
        d['max'] = 100
    return d        

"""
Returns a dict with the min and max playing time in minutes that games should be filtered on
Dict format: 3 fields
    - question: the question being answered [play_time]
    - min: minimum number of minutes of expected playtime to use in filter
    - max: maximum number of minutes of expected playtime to use in filter
"""
def player_time_response(text):
    d = {"question" : "play_time"}
    if text == 'Short (5-30 minutes)':
        d['min'] = 5
        d['max'] = 30
    elif text == 'Medium (30-60 minutes)':
        d['min'] = 30
        d['max'] = 60
    elif text == 'Long (60-120 minutes)':
        d['min'] = 60
        d['max'] = 120  
    elif text == 'Multiday (120+ minutes)':
        d['min'] = 120
        d['max'] = 100000  
    else:
        d['min'] = 5
        d['max'] = 100000
    return d     

"""
How to pull answers from Survey #1
Input: json file produced by the BGG Survey webhook
Returns: dict of responses with the following fields:
    - survey: name of survey (bgg_user)
    - user_id: user id (string) for BoardGameGeek.com
    - age: dict of age filters produced by player_age_response
    - num_players: dict of player number filters produced by player_num_response
    - play_time: dict of playing time filters produced by player_time_response
    - games: dict of games the player likes in the form of game_id : game_name (both strings)
"""
def get_bgg_survey_answers(json_data):
    d = {"survey" : "bgg_user"}
    d['id'] = json_data['event_id']
    user_id = json_data['form_response']['answers'][0]['text']    
    d['user_id'] = user_id    
    d['age'] = player_age_response(json_data['form_response']['answers'][1]['choice']['label'])
    d['num_players'] = player_num_response(json_data['form_response']['answers'][2]['choice']['label'])
    d['play_time'] = player_time_response(json_data['form_response']['answers'][3]['choice']['label'])    
    #Pull game collection using BGG API
    collection = bgg.collection(user_id, min_rating=7.0)
    game_list = {}
    for i in collection.items:
        game_list[str(i.id)] = i.name
    d['games'] = game_list
    return d

"""
How to pull answers from Survey #2
Input: json file produced by the Game Questionnaire webhook
Returns: dict of responses with the following fields:
    - survey: name of survey [questionnaire]    
    - age: dict of age filters produced by player_age_response
    - num_players: dict of player number filters produced by player_num_response
    - play_time: dict of playing time filters produced by player_time_response
    - games: dict of games the player likes in the form of game_id : game_name (both strings)
"""
def get_quest_survey_answers(json_data):
    d = {"survey" : "questionnaire"}    
    d['id'] = json_data['event_id']
    d['age'] = player_age_response(json_data['form_response']['answers'][0]['choice']['label'])
    d['num_players'] = player_num_response(json_data['form_response']['answers'][1]['choice']['label'])
    d['play_time'] = player_time_response(json_data['form_response']['answers'][2]['choice']['label'])    

    #Creating lookup dict of game title (string) : game id (string) for the 60 games in the questionnaire
    game_id = []
    game_title = []
    with open('data/survey_60games.csv', encoding = 'utf8') as infile:
        reader = csv.reader(infile, delimiter=',')
        for row in reader:                
            game_title.append(row[0])
            game_id.append(row[1])
    quest_games_lookup_dict = {game_title[i]: game_id[i] for i in range(len(game_id))}
    
    game_list = {}    
    for i in range(3, 9):
        game_title = json_data['form_response']['answers'][i]['choice']['label']
        game_id = quest_games_lookup_dict[game_title]
        #Exclude if they don't like any of the games, code '99999999'
        if game_id != '99999999':
            game_list[game_id] = game_title
    d['games'] = game_list
    return d