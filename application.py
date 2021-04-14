#!usr/bin/env python 

## Flask App
# This is where Flask handles the data from the recommendation engine and passes it around the site to the correct location

import json
import requests

from bs4 import BeautifulSoup
from flask import Flask, request, abort, render_template, make_response, session

from webhook_handler import get_bgg_survey_answers, get_quest_survey_answers
from recommender import recommender
from recommender_bgguser import recommender_bgguser


# EB looks for an 'application' callable by default.
application = Flask(__name__)
application.config.from_object(__name__)

BGG_GAME_LINK = "https://www.boardgamegeek.com/boardgame/"
BGG_API_LINK  = "https://www.boardgamegeek.com/xmlapi2/thing?id="

# Output file location.
surveyFileLoc  = '/tmp/survey_results.txt'
bgguserFileLoc = '/tmp/bgguser_results.txt'

print("WRITING OUT TMP FILES")
with open(surveyFileLoc, 'w') as fs:
    fs.write("test")

with open(bgguserFileLoc, 'w') as fb:
    fb.write("test")


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
def bgguserresults():
    global BGG_API_LINK
    global BGG_GAME_LINK

    print("BGGUSER_FILE_LOC:", bgguserFileLoc)
    with open(bgguserFileLoc, 'r') as f:
        json_data = json.load(f)
        
    # Add a list for the links
    game_links = []
    game_imgs  = []

    for game in json_data['game_id']:
        # Get the link to the game on bgg.
        game_links.append(BGG_GAME_LINK + str(game))

        # Get the link to the thumbnail
        api_link = BGG_API_LINK + str(game)
        resp = requests.get(api_link)
        soup = BeautifulSoup(resp.content, 'xml')
        thumbnail_link = soup.thumbnail.string
        game_imgs.append(thumbnail_link)        

    tag_class = []
    for level in json_data['level']:
        if level == 'Fits your taste': tag_class.append('is-danger')
        elif level == 'Very much fits your taste': tag_class.append('is-warning')
        elif level == 'Extremely fits your taste': tag_class.append('is-success')

    data = list(zip(json_data['game_id'], json_data['game_name'], json_data['level'], game_links, game_imgs, tag_class))
    return render_template("bgguserresults.html", data=data)


# BGG integration webhook handling
@application.route("/bgguserwebhook", methods=['GET','POST'])
def bgguserwebhook():
    if request.method == 'POST':
        bgg_json       = request.get_json()
        bgguser_result = get_bgg_survey_answers(bgg_json)
        user_score     = recommender_bgguser(bgguser_result)
        res            = make_response(user_score, 200)

        # Write out to tmp file.
        with open(bgguserFileLoc, 'w') as f:
            print("USER_SCORE:", user_score)
            f.write(user_score)

        return res

    if request.method == 'GET':
        return render_template("bgguserredirect.html")
        
    else:
        abort(400)




@application.route("/surveyresults")
def surveyresults():
    global BGG_API_LINK
    global BGG_GAME_LINK

    print("SURVEY_FILE_LOC:", surveyFileLoc)
    with open(surveyFileLoc, 'r') as f:        
        json_data = json.load(f)
        
    # Add a list for the links
    game_links = []
    game_imgs  = []
    for game in json_data['game_id']:
        # Get the link to the game on bgg.
        game_links.append(BGG_GAME_LINK + str(game))

        # Get the link to the thumbnail
        api_link = BGG_API_LINK + str(game)
        resp = requests.get(api_link)
        soup = BeautifulSoup(resp.content, 'xml')
        thumbnail_link = soup.thumbnail.string
        game_imgs.append(thumbnail_link)        

    tag_class = []
    for level in json_data['level']:
        if level == 'Similar': tag_class.append('is-danger')
        elif level == 'Very Similar': tag_class.append('is-warning')
        elif level == 'Extremely Similar': tag_class.append('is-success')

    data = list(zip(json_data['game_id'], json_data['game_name'], json_data['level'], game_links, game_imgs, tag_class))
    return render_template("surveyresults.html", data=data)


# Questionnaire webhook handling - receives the responses then calls the model.
@application.route("/questionnairewebhook", methods=['GET','POST'])
def questionnairewebhook():
    if request.method == 'POST':
        survey_json    = request.get_json(force=True)
        survey_result  = get_quest_survey_answers(survey_json)        
        recommend_game = recommender(survey_result)
        res            = make_response(recommend_game, 200)

        # Write out to tmp file.
        with open(surveyFileLoc, 'w') as f:
            print("RECOMMEND_GAME:", recommend_game)
            f.write(recommend_game)

        return res

    if request.method == 'GET':
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