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
neighborsModel = NearestNeighbors(n_neighbors=5, metric='cosine').fit(normalized_df)

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
  najslicnijiIndeksi = []

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
          dist, ind = neighborsModel.kneighbors(normalized_df.iloc[index].values.reshape(1, -1))
          najslicnijiIndeksi.extend(ind[0])

  # Filter out the songs from song_titles
  najslicnijiIndeksi = list(set(najslicnijiIndeksi))
  najslicnijiVektori = normalized_df[normalized_df.index.isin(najslicnijiIndeksi)]
  najslicnijiVektori = najslicnijiVektori.to_string(header=False, index=False)
  najslicnijePjesme = df[df.index.isin(najslicnijiIndeksi)]

  # Remove leading and trailing whitespace
  najslicnijiVektori = najslicnijiVektori.strip()
 
  # Split the string into lines
  lines = najslicnijiVektori.split('\n')
 
  # Split each line into a list of values
  vektori = [line.split() for line in lines]

  # Convert each value in the vektori to float
  vektori = [[float(value) for value in row] for row in vektori]

  # Convert your list of vectors to a 2D numpy array
  matrica_vektora = np.array(vektori)

  # Compute cosine similarity matrix
  sim = cosine_similarity(matrica_vektora)

 



  # Find indices of favorites in the most_similar_movies list
  indeksi = []
  for song_title in song_titles.song_titles:
      for idx, item in enumerate(najslicnijePjesme.iterrows()):
        if item[1]['name'].strip() == song_title:
          indeksi.append(idx)
          break

  # initialize a new list of zeros, length of movies / row in matrix
  avg_sim = [0] * len(najslicnijePjesme)

  # add values from each favorite movie 's similarity vector and calculate average
  for index in indeksi:
      for col, value in enumerate(sim[index]):
        avg_sim[col] += value / len(indeksi)

  # create pairs of movie index and calculated average similarity
  avg_sim = list(enumerate(avg_sim))
  avg_sim = sorted(avg_sim, key = lambda x: x[1], reverse = True)# Remove original picks
  avg_sim = [sim_pair
      for sim_pair in avg_sim
        if sim_pair[0] not in indeksi
  ]

  most_similar = avg_sim[0: 15]


  recommendations = []

  for i in range(len(most_similar)):
    row = najslicnijePjesme.iloc[most_similar[i][0]]
    song_name, song_album, song_artists = row['name'], row['album'], row['artists']
    artist_objects = [Artist(name=artist['name'], id=artist['id']) for artist in song_artists]
    recommendation = SuggestionModel(name=song_name, album=song_album, artists=artist_objects)
    recommendations.append(recommendation)

  return recommendations

 