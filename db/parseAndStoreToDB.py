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
 "track_number": "Int64", "disc_number": "Int64", "explicit": "boolean", "danceability": "Float32", "energy": "Float32", "key": "Int64", "loudness": "Float32",
  "mode": "Int64", "speechiness": "Float32", "acousticness": "Float32", "instrumentalness": "Float32", "liveness": "Float32", "valence": "Float32", "tempo": "Float32",
   "duration_ms": "Int64", "time_signature": "Float32", "year": "Int64", "release_date": "string"})

counter = 0

for index, row in tracks.iterrows():
    try:
        db.tracks.insert_one({
        "id": row['id'],
        "name": row['name'],
        "album": row['album'],
        "album_id": row['album_id'],
        "artists": create_artist_objects(row['artists'], row['artist_ids']),
        "track_number": row['track_number'],
        "disc_number": row['disc_number'],
        "explicit": row['explicit'],
        "danceability": row['danceability'],
        "energy": row['energy'],
        "key": row['key'],
        "loudness": row['loudness'],
        "mode": row['mode'],
        "speechiness": row['speechiness'],
        "acousticness": row['acousticness'],
        "instrumentalness": row['instrumentalness'],
        "liveness": row['liveness'],
        "valence": row['valence'],
        "tempo": row['tempo'],
        "duration_ms": row['duration_ms'],
        "time_signature": row['time_signature'],
        "year": row['year'],
        "release_date": row['release_date']
    })
    except:
        print('Invalid row: ')
        print(row)

    # counter = counter + 1
    # if counter == 10:
    #     break
