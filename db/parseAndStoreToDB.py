from pymongo import MongoClient
import pandas as pd
import json


# Connect to the database
client=MongoClient()
client = MongoClient('localhost', port=27017, username="admin", password="password")
db = client["tempo-trove-db"]

def create_artist_objects(names, ids):
   # Remove brackets and quotes
   names = names.replace("[", "").replace("]", "").replace("'", "")
   ids = ids.replace("[", "").replace("]", "").replace("'", "")

   # Split the strings into lists
   names_list = names.split(", ")
   ids_list = ids.split(", ")

   # Create a list of dictionaries
   artists = []
   for name, id in zip(names_list, ids_list):
       artist = {'name': name, 'id': id}
       artists.append(artist)

   return artists

# read and combine three csv files

tracks = pd.read_csv("tracks_features.csv", dtype={"id": "string", "name": "string", "album": "string", "album_id": "string", "artists": object, "artist_ids": object,
 "explicit": "boolean", "norm_danceability": "Float32", "norm_energy": "Float32", "norm_key": "Float32", "norm_loudness": "Float32",
  "norm_mode": "Float32", "norm_speechiness": "Float32", "norm_acousticness": "Float32", "norm_instrumentalness": "Float32", "norm_liveness": "Float32", "norm_valence": "Float32", "norm_tempo": "Float32",
   "norm_duration": "Float32", "norm_time_signature": "Float32", "norm_year": "Float32"})

counter = 0

for index, row in tracks.iterrows():
    try:
        db.tracks.insert_one({
        "id": row['id'],
        "name": row['name'],
        "album": row['album'],
        "album_id": row['album_id'],
        "artists": create_artist_objects(row['artists'], row['artist_ids']),
        "explicit": int(row['explicit']),
        "danceability": row['norm_danceability'],
        "energy": row['norm_energy'],
        "key": row['norm_key'],
        "loudness": row['norm_loudness'],
        "mode": row['norm_mode'],
        "speechiness": row['norm_speechiness'],
        "acousticness": row['norm_acousticness'],
        "instrumentalness": row['norm_instrumentalness'],
        "liveness": row['norm_liveness'],
        "valence": row['norm_valence'],
        "tempo": row['norm_tempo'],
        "duration_ms": row['norm_duration'],
        "time_signature": row['norm_time_signature'],
        "year": row['norm_year']
    })
    except Exception as e:
        print('Invalid row: ')
        print(e)
        print(row)

    counter = counter + 1
    if counter == 20:
       break
