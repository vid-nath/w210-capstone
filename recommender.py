import json
import csv
import turicreate as tc
'''
recommend based on games provided in questionnaire and filter recommended games by questionnaire answers,
input: json file get from webhook
output: json with game_id and confidence_score 
'''


def recommender(dataset):
    #MODEL_PATH  = 'game_rec_model_2k'
    MODEL_PATH  = 'game_rec_model'
    MODEL       = tc.load_model(MODEL_PATH)
    new_obs_data = json.loads(dataset)
    new_obs_data_new = [int(i) for i in list(new_obs_data["games"].keys())]
    filter_condt     = tc.SFrame({"age_min": [new_obs_data["age"]["min"]],
                                   "age_max": [new_obs_data["age"]["max"]],
                                   "num_players_min": [new_obs_data["num_players"]["min"]],
                                   "num_players_max": [new_obs_data["num_players"]["max"]],
                                   "play_time_min": [new_obs_data["play_time"]["min"]],
                                   "play_time_max": [new_obs_data["play_time"]["max"]]})

     # Load in the model from a saved bin file, then read in the game data adn combine it with the passed in data.
    print("Loading in model and get recommended items...", file=sys.stdout)
    df_items  = pd.read_csv('data/game_info_750.csv')
    rec_items = MODEL.recommend_from_interactions(new_obs_data_new, k=50)
    
     # Select 50 recommended games' info.
    df_rec_game_info = df_items.loc[df_items['game_id'].isin(rec_items['game_id'])]
    
     # Filter out game based on user answers.
    df_items_filter = df_rec_game_info[(df_rec_game_info['age_min']  > filter_condt['age_min'])       &
                                        (df_rec_game_info['avg_time'] > filter_condt['play_time_min']) & 
                                        (df_rec_game_info['avg_time'] < filter_condt['play_time_max'])]

#     # Convert rec_items to a dataframe.
    df_rec_items = rec_items.to_dataframe()

#     # Output the top 5 games.
    output        = df_rec_items.loc[df_rec_items['game_id'].isin(df_items_filter.game_id)].sort_values('score', ascending=False).head(5)
    json_output   = json.dumps({"event_id":new_obs_data["id"], "game_id": list(output["game_id"]), "score": list(output["score"])})
#     # if output_file:
    #open(output_path, "w").write(json_output) # Write out json to a file to read in later.
    return json_output
