#!usr/bin/env python
# Encoding: UTF-8

## Modeling Pipeline
# Here we ingest the cleaned data (via an IPython Notebook) and run it through the pipeline for training, testing, validating, and saving our model. Additionally, this pipeline will intake and apply user data to load models for recommendations.
# Note: This code should only be run once since it will generate the model used everywhere else in the code.

import pandas as pd
import turicreate as tc

# TODO run with full data once, save off - then commit and only load thereafter - consolidate into one file.

# Note that these might not exist in the local environment, so make sure that they are available.
train_path = 'data/training_data_3column_750.csv'
info_path  = 'data/game_info_750.csv'
model_name = 'game_rec_model'


# Mostly unneeded unless pruning data.
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
def model_data(path=train_path, name=model_name, pruning=False):
    if pruning:
        path = 'data/training_data_minified.csv'
        name = 'game_rec_model_minified'
        prune_pct  = 0.275
        prune_data(path=path, prune_pct=prune_pct)

    print("\nRunning modeling with path: " + path + " and name: " + name)
    actions = tc.SFrame.read_csv(path)

    print("Filtering data")
    actions = actions[['game_id','user_id','rating']]
    model   = tc.recommender.item_similarity_recommender.create(actions, 'user_id', 'game_id', target='rating', similarity_type='cosine')

    # Save the model.
    print("Saving the model to:", name)
    model.save(name)


# Main execution. Set pruning to True if need to reduce the training data size (prune the data).
path = train_path
name = model_name
model_data(path, name, pruning=False)