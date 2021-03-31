#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

from flask import Flask, request, abort, render_template, Response, jsonify, make_response
#from flask_cors import CORS

import json
import os
from flask.templating import render_template_string
import pandas as pd
import sys
from webhook_handler import get_bgg_survey_answers, get_quest_survey_answers
from recommender import recommender
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

@application.route("/results")
def results():
    # This is something that sort of works - need to figure out how to embed html via flask into the html page.
    # results = pd.read_json('data/json_test_output.json')
    # resHtml = results.to_html(render_links=True, justify='center')
    return render_template("results.html") #, inData=results)


# BGG integration webhook handling
@application.route("/bgguserwebhook", methods=['POST'])
def bgguserwebhook():
    if request.method == 'POST':
        bgg_json       = request.get_json()
        bgguser_result = get_bgg_survey_answers(bgg_json)
        #res = make_response(jsonify(bgguser_result), 200)
        res            = make_response(bgguser_result, 200)
        return res

    else:
        abort(400)


# Questionnaire webhook handling
@application.route("/questionnairewebhook", methods=['GET','POST'])
def questionnairewebhook():
    if request.method == 'POST':
        survey_json    = request.get_json(force=True)
        survey_result  = get_quest_survey_answers(survey_json)        
        recommend_game = recommender(survey_result)
        res            = make_response(recommend_game, 200)
        return res

    else:
        abort(400)
         

# Run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug        = True
    application.use_reloader = True
    application.run()