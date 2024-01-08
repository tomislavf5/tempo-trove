from typing import List
from pymongo import MongoClient
from fastapi import FastAPI, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from scipy.spatial import distance
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np

app = FastAPI()

# Connect to the database
client=MongoClient()
client = MongoClient('localhost', port=27017, username="admin", password="password")
db = client["tempo-trove-db"]
col = db['tracks']


data = list(col.find())
df = pd.DataFrame(data)

feature_cols=['explicit', 'mode', 'speechiness', 'key', 'acousticness',
              'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms',
              'time_signature', 'year', 'energy', 'danceability', 'loudness',]

# Assuming df is your DataFrame and feature_cols are your feature columns
normalized_df = df[feature_cols].copy()

# Fit a NearestNeighbors model to the data
neighborsModel = NearestNeighbors(n_neighbors=1500, metric='cosine').fit(normalized_df)

# Create a new column 'album_name' in the dataframe that combines 'name' and 'album'
df['album_name'] = df['name'] + ' - ' + df['album']

# Create a new series that maps song names along with their album names to their indices
indices = pd.Series(df.index, index=df['album_name']).drop_duplicates()

# Mongo id schema
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        handler(field_schema.update(type="string"))

# Autocomplete model
class Artist(BaseModel):
  name: str
  id: str

class AutocompleteModel(BaseModel):
  id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
  name: str = Field(...)
  album: str = Field(...)
  artists: List[Artist] = Field(...)

  class Config:
      populate_by_name = True
      arbitrary_types_allowed = True
      json_encoders = {ObjectId: str}

# Suggestion model
class SuggestionModel(BaseModel):
  id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
  name: str = Field(...)
  album: str = Field(...)
  artists: List[Artist] = Field(...)

  class Config:
      populate_by_name = True
      arbitrary_types_allowed = True
      json_encoders = {ObjectId: str}

#  cors
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Returns the first 10 tracks whose name satisfies the search string
@app.get("/search", response_model=List[AutocompleteModel])
def search_tracks(search: str = ""):
   print(search)
   tracks = list(db.tracks.find({"name": {"$regex": search.lower(), "$options" :'i'}}, {"name": 1, "album": 1, "artists": 1}).limit(20))
   print(tracks)
   return tracks

class SongTitles(BaseModel):
  song_titles: List[str]
  albums: List[str]
  

@app.post("/suggest_songs", response_model=List[SuggestionModel])
def generate_recommendation(song_titles: SongTitles):
 # Initialize an empty list to store the scores
 scores = []

 # Create a vector representation for each song
 song_vectors = df[feature_cols].values

 # Fit the Nearest Neighbors model
 neighborsModel = NearestNeighbors()
 neighborsModel.fit(normalized_df)
 print("Model fitted successfully.")

 # Find the nearest neighbors for each song
 for song_title, album_title in zip(song_titles.song_titles, song_titles.albums):
   full_title = song_title + ' - ' + album_title
   if full_title not in indices.index:
       print(f"No song titled '{full_title}' found.")
   else:
        print(f"Found song titled '{full_title}'.")

        # Get song index
        index = indices[full_title]
        # Calculate the score for the song
        dist, ind = neighborsModel.kneighbors(normalized_df.iloc[index].values.reshape(1, -1), n_neighbors=len(normalized_df)-1)
        scores.extend(zip(ind[0], dist[0]))

 # Filter out the songs from song_titles
 filtered_scores = [(score[0], score[1]) for score in scores if df['name'].iloc[score[0]] not in song_titles.song_titles]

 # Sort the scores
 sorted_scores = sorted(filtered_scores, key=lambda x: x[1], reverse=False)
 print("Sorted scores successfully.")

 # Select the top-10 recommended songs
 top_songs_index = [score[0] for score in sorted_scores[:10]]

 # Convert the pandas.Series object to a list of Artist objects
 artists = [[Artist(name=artist['name'], id=artist['id']) for artist in df['artists'].iloc[i]] for i in top_songs_index]

 # Create a list of song names
 song_names = [df['name'].iloc[i] for i in top_songs_index]

 # Pass the list of Artist objects and song names to the AutocompleteModel
 top_songs=[SuggestionModel(id=df['_id'].iloc[i], name=song_names[i], album=df['album'].iloc[i], artists=artists[i]) for i in range(len(artists))]
 return top_songs