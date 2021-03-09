#!usr/bin/env python
# Encoding: UTF-8

## Modeling Pipeline
# Here we ingest the cleaned data (via an IPython Notebook) and run it through the pipeline for training, testing, validating, and saving our model. Additionally, this pipeline will intake and apply user data to load models for recommendations.
# Note: This code should only be run once since it will generate the model used everywhere else in the code.

import boto3
import os
import sys
import pandas as pd
import turicreate as tc

# TODO run with full data once, save off - then commit and only load thereafter - consolidate into one file.

if str(sys.argv[0]) == "RUN_MODEL":
    actions  = tc.SFrame.read_csv('data/training_data_3column_750.csv')
    items    = tc.SFrame.read_csv('data/game_info_750.csv')
    df_items = pd.read_csv('data/game_info_750.csv')

    actions       = actions[['game_id','user_id','rating']]
    model         = tc.recommender.item_similarity_recommender.create(actions,'user_id','game_id',target='rating',similarity_type='cosine')
    similar_items = model.get_similar_items([1,3],k=5)

    # Save the model.
    model.save('game_rec_model')

else:
    print("Not running modeling.")