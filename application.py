#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

from flask import Flask, request, abort, render_template, Response, jsonify, make_response
#from flask_cors import CORS

import json
import os
import pandas as pd
import sys
from webhook_handler import get_bgg_survey_answers, get_quest_survey_answers
#import turicreate as tc


# EB looks for an 'application' callable by default.
application = app = Flask(__name__)
#CORS(application)

@application.route("/")
def home():
    return render_template("index.html")

@application.route("/index")
def index():
    return render_template("index.html")

@application.route("/product")
def product():
    return render_template("product.html")

@application.route("/bgguser")
def bgguser():
    return render_template("bgguser.html")

@application.route("/people")
def people():
    return render_template("people.html")

@application.route("/result")
def result():
    return render_template("result.html")

#BGG integration webhook handling
@app.route("/bgguserwebhook", methods=['POST'])
def bgguserwebhook():
     if request.method == 'POST':
         bgg_json = request.get_json()
         bgguser_result = get_bgg_survey_answers(bgg_json)
         #res = make_response(jsonify(bgguser_result), 200)
         res = make_response(bgguser_result, 200)
         return res
     else:
         abort(400)

#Questionnaire webhook handling
@app.route("/questionnairewebhook", methods=['POST'])
def questionnairewebhook():
     if request.method == 'POST':
         survey_json = request.get_json()
         survey_result = get_quest_survey_answers(survey_json)         
         res = make_response(survey_result, 200)
         return res
     else:
         abort(400)
         
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug        = True
    application.use_reloader = True
    application.run()

# # Main
# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=True)

# # Setup file-wide variables.
# MODEL_PATH  = 'game_rec_model_min'
# MODEL       = tc.load_model(MODEL_PATH)
# #GAME_INFO   = pd.read_csv('data/game_info_full.csv')
# GAME_LOOKUP = pd.read_csv('game_lookup.csv')

# def game_lookup(inId):
#     game_data = GAME_LOOKUP[GAME_LOOKUP.game_id == inId]
#     print(game_data.describe, file=sys.stdout)
#     return game_data['game_id']


# # Recommend method to clean and provide the recommended values.
# # Import json of user's answers and run model prediction.
# #@app.route("/recommend", methods=['GET'])

# def recommend():#output_file=False, output_path='json_test_output.json'):
#     # TODO - hook to the onSubmit call to Typeform results - needs to pull from online
#     print("Reading questionnaire input...", file=sys.stdout)
#     json_file_path = "questionnaire_result.json"

#     with open(json_file_path, 'r') as j:
#          new_obs_data = json.loads(j.read())

#     print("Filtering data using questionnaire input...", file=sys.stdout)
#     new_obs_data_new = [int(i) for i in list(new_obs_data["games"].keys())]
#     filter_condt     = tc.SFrame({"age_min": [new_obs_data["age"]["min"]],
#                                   "age_max": [new_obs_data["age"]["max"]],
#                                   "num_players_min": [new_obs_data["num_players"]["min"]],
#                                   "num_players_max": [new_obs_data["num_players"]["max"]],
#                                   "play_time_min": [new_obs_data["play_time"]["min"]],
#                                   "play_time_max": [new_obs_data["play_time"]["max"]]})

#     # Load in the model from a saved bin file, then read in the game data adn combine it with the passed in data.
#     print("Loading in model and get recommended items...", file=sys.stdout)
#     df_items  = pd.read_csv('game_info_750.csv')
#     rec_items = MODEL.recommend_from_interactions(new_obs_data_new, k=50)
    
#     # Select 50 recommended games' info.
#     df_rec_game_info = df_items.loc[df_items['game_id'].isin(rec_items['game_id'])]
    
#     # Filter out game based on user answers.
#     df_items_filter = df_rec_game_info[(df_rec_game_info['age_min']  > filter_condt['age_min'])       &
#                                        (df_rec_game_info['avg_time'] > filter_condt['play_time_min']) & 
#                                        (df_rec_game_info['avg_time'] < filter_condt['play_time_max'])]

#     # Convert rec_items to a dataframe.
#     df_rec_items = rec_items.to_dataframe()

#     # Output the top 5 games.
#     output        = df_rec_items.loc[df_rec_items['game_id'].isin(df_items_filter.game_id)].sort_values('score', ascending=False).head(5)
#     json_output   = json.dumps({"game_id": list(output["game_id"]), "score": list(output["score"])})
#     # if output_file:
#     #     open(output_path, "w").write(json_output) # Write out json to a file to read in later.
#     return json_output



# # Page redirects.
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/product")
# def product():
#     return render_template("product.html")


# @app.route("/bgguser", methods=['GET'])
# def bgguser():
#     print("Response: " + request.json, file=sys.stdout)
#     return Response(status=200)


# # @app.route("/questionnaire", methods=['GET'])
# # def questionnaire():
# #     print("Response: " + request.json, file=sys.stdout)
# #     return Response(status=200)


# # TODO find more efficient way of using json_output from recommend method to read in the data.
# @app.route("/questionnaire", methods=['GET'])
# def questionnaire():
#     json_output = recommend()
#     json_data   = json.loads(json_output)

#     print("json_data: ", json_data, file=sys.stdout)
#     game_ids = json_data['game_id']
#     print("game_ids: ", game_ids, file=sys.stdout)
#     games_dict = {}
#     for id in game_ids:
#         game_data = game_lookup(id)
#         print("game_data: ", game_data, file=sys.stdout)


#     return render_template("questionnaire.html", in_data=game_ids)

# # Main
# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=True)