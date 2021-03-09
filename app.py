#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_s3 import FLASKS3

import json
import os
import sys
import turicreate as tc

app = Flask(__name__)
app.config['FLASKS3_BUCKET_NAME'] = 'w210-capstone'
s3 = FLASKS3(app)
CORS(app)

# Simple method to retrieve a pre-saved model
def load_model():
    return tc.load_model('http://s3.amazonaws.com/w210-capstone/game_rec_model')

# S3 Connection
@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')

  file_name = request.args.get('file_name')
  file_type = request.args.get('file_type')

  s3 = boto3.client('s3')

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })

# Recommend method to clean and provide the recommended values.
# Import json of user's answers and run model prediction.
@app.route("/recommend", methods=['GET'])
def recommend():
    # TODO - hook to the onSubmit call to Typeform results - needs to pull from online
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
@app.route("/", methods=['GET'])
def index():
    json_data = recommend()
    return render_template("index.html", table=json_data)

@app.route("/product")
def product():
    return render_template("product.html")



@app.route("/results", methods=['GET'])
def results():
    json_data = recommend()
    return json_data



#APP_FOLDER = os.path.dirname(os.path.realpath(__file__))

# Main
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


"""
TODO: 
- Clean up recommend code:
    - Remove data processing and data folders
    - Update game_rec_model folder with the one from main repo
    - Redeploy and test on heroku
- Setup webhooks with Flask and Typeform
    - Capture output json from model and from Typeform submit
    - Integrate Typeform results processing

- Copy over the current webform onto the ischool domain and fix up site there for "live hosting"

"""