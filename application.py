#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

import json
import os

from flask import Flask, request, redirect, url_for, abort, render_template, make_response, session

from webhook_handler import get_bgg_survey_answers, get_quest_survey_answers
from recommender import recommender
from recommender_bgguser import recommender_bgguser


# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.config.from_object(__name__)

# Set a secret key for the session.
key = os.urandom(24).hex()
application.secret_key = key
application.testing    = True


# Output file location.
surveyFileLoc  = '/tmp/survey_results.txt'
bgguserFileLoc = '/tmp/bgguser_results.txt'
newFile1       = open(surveyFileLoc, 'w')
newFile1       = open(bgguserFileLoc, 'w')



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



@application.route("/bgguserresults")
def bggusersurveyresults():
    print("LOADING BGGUSER RESULTS")
    with open(bgguserFileLoc, 'r') as f:
        print("READING IN TMP FILE:", f)
        json_data = json.load(f)
        
    print("JSON_DATA:", json_data)
    data = list(zip(json_data['game_name'], json_data['level']))
    return render_template("surveyresults.html", data=data)


# BGG integration webhook handling
@application.route("/bgguserwebhook", methods=['GET','POST'])
def bgguserwebhook():
    if request.method == 'POST':
        print("GETTING BGGUSER RESULTS")
        bgg_json       = request.get_json()
        bgguser_result = get_bgg_survey_answers(bgg_json)
        user_score     = recommender_bgguser(bgguser_result)
        res            = make_response(user_score, 200)

        # Write out to tmp file.
        with open(bgguserFileLoc, 'w') as f:
            print("WRITING SCORE:", user_score)
            f.write(user_score)
            print("OUTPUTFILE:", f)

        return res

    if request.method == 'GET':
        print("REDIRECTING TO REDIRECT PAGE")
        return render_template("bgguserredirect.html")
        
    else:
        abort(400)


@application.route("/surveyresults")
def surveyresults():
    print("LOADING SURVEY RESULTS")
    with open(surveyFileLoc, 'r') as f:
        print("READING IN TMP FILE:", f)
        json_data = json.load(f)
        
    print("JSON_DATA:", json_data)
    data = list(zip(json_data['game_name'], json_data['level']))
    return render_template("surveyresults.html", data=data)


# Questionnaire webhook handling - receives the responses then calls the model.
@application.route("/questionnairewebhook", methods=['GET','POST'])
def questionnairewebhook():
    if request.method == 'POST':
        print("GETTING POST RESULTS")
        survey_json    = request.get_json(force=True)
        survey_result  = get_quest_survey_answers(survey_json)        
        recommend_game = recommender(survey_result)
        res            = make_response(recommend_game, 200)

        # Write out to tmp file.
        with open(surveyFileLoc, 'w') as f:
            print("WRITING:", recommend_game)
            f.write(recommend_game)
            print("OUTPUTFILE:", f)

        return res

    if request.method == 'GET':
        print("REDIRECTING TO REDIRECT PAGE")
        return render_template("surveyredirect.html")
        
    else:
        abort(400)



# Run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug        = True
    application.use_reloader = True
    application.run()