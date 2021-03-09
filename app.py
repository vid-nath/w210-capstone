#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import recommendation

import json
import os
import sys
import turicreate as tc

app = Flask(__name__)
CORS(app)

# Recommend method to clean and provide the recommended values.
# Import json of user's answers and run model prediction.
@app.route("/recommend", methods=['GET'])
def recommend():
    json_file_path = "data/questionnaire_result.json"

    with open(json_file_path, 'r') as j:
         new_obs_data = json.loads(j.read())


    new_obs_data_new = [int(i) for i in list(new_obs_data["games"].keys())]
    filter_condt     = tc.SFrame({"age_min": [new_obs_data["age"]["min"]],
                                  "age_max": [new_obs_data["age"]["max"]],
                                  "num_players_min": [new_obs_data["num_players"]["min"]],
                                  "num_players_max": [new_obs_data["num_players"]["max"]],
                                  "play_time_min": [new_obs_data["play_time"]["min"]],
                                  "play_time_max": [new_obs_data["play_time"]["max"]]})
    
    recommend_items = recommendation.rec_model.recommend_from_interactions(new_obs_data_new, k=50)
    
    # Select 50 recommended games' info.
    df_rec_game_info = recommendation.df_items.loc[recommendation.df_items['game_id'].isin(recommend_items['game_id'])]
    
    # Filter out game based on user answers.
    df_items_filter = df_rec_game_info[(df_rec_game_info['age_min']  > filter_condt['age_min'])       &
                                       (df_rec_game_info['avg_time'] > filter_condt['play_time_min']) & 
                                       (df_rec_game_info['avg_time'] < filter_condt['play_time_max'])]

    # Convert recommend_items to a dataframe.
    df_recommend_items=recommend_items.to_dataframe()

    # Output the top 5 games.
    output      = df_recommend_items.loc[df_recommend_items['game_id'].isin(df_items_filter.game_id)].sort_values('score', ascending=False).head(5)
    json_output = json.dumps({"game_id": list(output["game_id"]), "score": list(output["score"])})
    return json_output


# Page redirects.
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/product")
def product():
    return render_template("product.html")

@app.route("/results", methods=['GET'])
def results():
    json_data = recommend()
    return json_data


    # if request.method == 'POST':
    #     # TODO need to add Typeform output into the JSON file 
    #     print("Getting JSON Data")
    #     json_data = recommend()
    #     print(json_data)
    #     return render_template('index.html', table=json_data)




# @app.route("/process")
# def segment():
#     return render_template("process.html")


# @app.route("/people")
# def score():
#     return render_template("people.html")   




#APP_FOLDER = os.path.dirname(os.path.realpath(__file__))

# Main
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)