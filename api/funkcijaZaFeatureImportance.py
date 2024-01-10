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
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

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

normalized_df = df[feature_cols].copy()

neighborsModel = NearestNeighbors(n_neighbors=1500, metric='cosine').fit(normalized_df)

df['album_name'] = df['name'] + ' - ' + df['album']

indices = pd.Series(df.index, index=df['album_name']).drop_duplicates()

# Initialize a random forest regressor
rf = RandomForestRegressor(random_state=42)

# Train the model
rf.fit(normalized_df, normalized_df.index)

# Get feature importances
importances = rf.feature_importances_

# Sort the feature importance in descending order
sorted_indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")
for f in range(normalized_df.shape[1]):
 print("%d. %s (%f)" % (f + 1, normalized_df.columns[sorted_indices[f]], importances[sorted_indices[f]]))

# Plot the feature importance
plt.figure()
plt.title('Feature Importance')
plt.bar(range(normalized_df.shape[1]), importances[sorted_indices], align='center')
plt.xticks(range(normalized_df.shape[1]), normalized_df.columns[sorted_indices], rotation=90)
plt.tight_layout()
plt.show()

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

 avg_sim_values = []

 for num_neighbors in range(2, 5):
    neighborsModel = NearestNeighbors(n_neighbors=num_neighbors)
    neighborsModel.fit(normalized_df)
    najslicnijiIndeksi = []
    for song_title, album_title in zip(song_titles.song_titles, song_titles.albums):
        full_title = song_title + ' - ' + album_title
        if full_title not in indices.index:
            print(f"No song titled '{full_title}' found.")
        else:
            print(f"Found song titled '{full_title}'.")
            index = indices[full_title]
            dist, ind = neighborsModel.kneighbors(normalized_df.iloc[index].values.reshape(1, -1), n_neighbors=num_neighbors)
            najslicnijiIndeksi.extend(ind[0])
    najslicnijiIndeksi = list(set(najslicnijiIndeksi))
    najslicnijiVektori = normalized_df[normalized_df.index.isin(najslicnijiIndeksi)]
    najslicnijiVektori = najslicnijiVektori.to_string(header=False, index=False)
    najslicnijePjesme = df[df.index.isin(najslicnijiIndeksi)]
    najslicnijiVektori = najslicnijiVektori.strip()
    lines = najslicnijiVektori.split('\n')
    vektori = [line.split() for line in lines]
    vektori = [[float(value) for value in row] for row in vektori]
    matrica_vektora = np.array(vektori)
    sim = cosine_similarity(matrica_vektora)
    indeksi = []
    for song_title in song_titles.song_titles:
        for idx, item in enumerate(najslicnijePjesme.iterrows()):
            if item[1]['name'].strip() == song_title:
              indeksi.append(idx)
              break
    avg_sim = [0] * len(najslicnijePjesme)
    for index in indeksi:
        for col, value in enumerate(sim[index]):
            avg_sim[col] += value / len(indeksi)
    avg_sim = list(enumerate(avg_sim))
    avg_sim = sorted(avg_sim, key = lambda x: x[1], reverse = True)
    avg_sim = [sim_pair for sim_pair in avg_sim if sim_pair[0] not in indeksi]
    if len(avg_sim) > 0:
      avg_sim = sum(avg_sim[i][1] for i in range(len(avg_sim))) / len(avg_sim)
    else:
      avg_sim = 0
    avg_sim_values.append(avg_sim)


 # Plot the average similarity values
 plt.figure(figsize=(10, 6))
 plt.plot(range(len(avg_sim_values)), avg_sim_values, marker='o')
 plt.xlabel('Number of Neighbors')
 plt.ylabel('Average Similarity')
 plt.title('Average Similarity vs Number of Neighbors')
 plt.grid(True)
 plt.show()


 recommendations = []
 for i in range(len(avg_sim_values)):
    row = najslicnijePjesme.iloc[avg_sim_values[i][0]]
    song_name, song_album, song_artists = row['name'], row['album'], row['artists']
    artist_objects = [Artist(name=artist['name'], id=artist['id']) for artist in song_artists]
    recommendation = SuggestionModel(name=song_name, album=song_album, artists=artist_objects)
    recommendations.append(recommendation)
 return recommendations




