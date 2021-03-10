#!usr/bin/env python
# Encoding: UTF-8

## Modeling Pipeline
# Here we ingest the cleaned data (via an IPython Notebook) and run it through the pipeline for training, testing, validating, and saving our model. Additionally, this pipeline will intake and apply user data to load models for recommendations.
# Note: This code should only be run once since it will generate the model used everywhere else in the code.

import os
import sys
import pandas as pd
import turicreate as tc

# TODO run with full data once, save off - then commit and only load thereafter - consolidate into one file.

train_path = 'data/training_data_3column_750.csv'
info_path  = 'data/game_info_750.csv'
model_name = 'game_rec_model_full'
github_upload_limit_bytes = 95.0 * 1024 * 1024 # 95 mb * 1024 kb/mb * 1024 b/kb - this estimates lower than 100 hard limit



# Method to prune data down to a percentage of the original.
def prune_data(path=train_path, prune_pct=0.1):
    print("\nPruning csv data from:", path)
    full_data = pd.read_csv(path)
    print(full_data.describe)

    max_pct     = 100.0
    prune_limit = int(max_pct * prune_pct) # Nominally 10 -> 10% of data    
    print("Pruning data with limit:", str(prune_limit))

    min_data     = full_data[full_data.index % max_pct < prune_limit]
    print(min_data.describe)
    
    min_data_mem_size_bytes = min_data.memory_usage(index=True).sum()
    print("Data within limits:", str(min_data_mem_size_bytes < github_upload_limit_bytes))
    
    # Save the data to a csv.
    min_data.to_csv('data/training_data_minified.csv')



# Method to model the data and save the model.
def model_data(path=train_path, name=model_name):
    print("\nRunning modeling with path: " + path + " and name: " + name)
    actions = tc.SFrame.read_csv(path)

    print("Filtering data")
    actions = actions[['game_id','user_id','rating']]
    model   = tc.recommender.item_similarity_recommender.create(actions, 'user_id', 'game_id', target='rating', similarity_type='cosine')

    # Save the model.
    print("Saving the model to:", name)
    model.save(name)



# Main execution.
print("System arguments:", str(sys.argv))

# Minify the data.
path = train_path
name = model_name

if str(sys.argv[1]) == "MIN":
    print("\nMinifying data...")
    prune_pct  = 0.35
    prune_data(prune_pct=prune_pct)
    print("Changing train_path and model name...")
    path = 'data/training_data_minified.csv'
    name = 'game_rec_model_min'

# Model the data.
if str(sys.argv[2]) == "MODEL":
    print("\nTrain_path:", path)
    print("Model_name:", name)
    model_data(path, name)


## DEPRECATED - use for reference
# # Reduce data size.
# def prune_data(path, prune=100):
#     print("Reading in csv data from:", path)
#     full_data = pd.read_csv(path)
#     print(full_data.describe)
    
#     # Get full memory data and set ratio for accepted data.
#     full_data_mem_bytes = full_data.memory_usage(index=True).sum()
#     upload_ratio = github_upload_limit_bytes / full_data_mem_bytes * 1.0

#     # check values
#     print("Full data size:", str(full_data_mem_bytes))
#     print("github size:", str(github_upload_limit_bytes))
#     print("data size ratio:", str(upload_ratio))

#     prune_limit = int(upload_ratio * prune)
#     print("List limit:", str(prune_limit))
#     min_data  = full_data[full_data.index % prune < prune_limit]
#     print(min_data.describe)
#     min_data.to_csv('data/min_training_data.csv')

 # Main execution
# print("System args: ", str(sys.argv))
# train_path = 'data/training_data_3column_750.csv'

# # Set up paths and names
# if str(sys.argv[1]) == "MIN":
#     print("pruning then minifying data")
#     prune_data(train_path)
#     train_path = 'data/min_training_data.csv'
#     model_name = 'game_rec_model_minified'


# if str(sys.argv[2]) == "MODEL":
#     print("running model")
#     actions  = tc.SFrame.read_csv(train_path)
#     items    = tc.SFrame.read_csv(info_path)
#     df_items = pd.read_csv(info_path)

#     actions       = actions[['game_id','user_id','rating']]
#     model         = tc.recommender.item_similarity_recommender.create(actions,'user_id','game_id',target='rating',similarity_type='cosine')
#     similar_items = model.get_similar_items([1,3],k=5)

#     # Save the model.
#     model.save(model_name)