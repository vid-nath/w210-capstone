#!usr/bin/env python
# Encoding: UTF-8

## Modeling Pipeline
# Here we ingest the cleaned data (via an IPython Notebook) and run it through the pipeline for training, testing, validating, and saving our model. Additionally, this pipeline will intake and apply user data to load models for recommendations.

import boto3
import caserec
import h5py
import json
import pickle
import sklearn
import tables

import numpy as np
import pandas as pd
import turicreate as tc

actions  = tc.SFrame.read_csv('data/training_data_3column_750_minified.csv')
items    = tc.SFrame.read_csv('data/game_info_750.csv')
df_items = pd.read_csv('data/game_info_750.csv')

actions       = actions[['game_id','user_id','rating']]
model         = tc.recommender.item_similarity_recommender.create(actions,'user_id','game_id',target='rating',similarity_type='cosine')
similar_items = model.get_similar_items([1,3],k=5)

# Save the model.
model.save('game_rec_model')

# Load the model.
rec_model = tc.load_model('game_rec_model')

# Try with random user input data
new_obs_data = tc.SFrame({'user_id' : ['survey', 'survey', 'survey', 'survey', 'survey'],
                          'game_id' : ['4098', '9216', '475', '148228', '68448']})

recommend_games = rec_model.recommend_from_interactions([4098,9216,475])

new_obs_data_1    = [362, 3, 9440]
recommend_games_1 = rec_model.recommend_from_interactions(new_obs_data_1,k=50)
#recommend_games_1 = rec_model.recommend_from_interactions([362,3,9440],k=50)


my_list_of_items = [130802, 8577, 362, 30549, 31]
similar_items    = rec_model.get_similar_items(my_list_of_items,k=20)
