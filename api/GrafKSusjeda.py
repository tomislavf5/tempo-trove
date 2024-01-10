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
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import KNeighborsClassifier

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
    najslicnijiIndeksi = []
    song_vectors = df[feature_cols].values

    n_neighbors_values = [100, 300, 600, 900, 1200, 1500, 1800, 2100, 2500, 4000, 6000]
    avg_similarities = {}

    for n_neighbors in n_neighbors_values:
        print("current n: ", n_neighbors)
        neighborsModel = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        neighborsModel.fit(normalized_df)

        avg_similarity = 0
        for song_title, album_title in zip(song_titles.song_titles, song_titles.albums):
            full_title = song_title + ' - ' + album_title
            if full_title not in indices.index:
                continue

            index = indices[full_title]
            dist, ind = neighborsModel.kneighbors(normalized_df.iloc[index].values.reshape(1, -1), n_neighbors=n_neighbors)
            najslicnijiIndeksi.extend(ind[0])

        najslicnijiIndeksi = list(set(najslicnijiIndeksi))
        najslicnijiVektori = normalized_df[normalized_df.index.isin(najslicnijiIndeksi)]
        najslicnijePjesme = df[df.index.isin(najslicnijiIndeksi)]

        najslicnijiVektori = najslicnijiVektori.to_string(header=False, index=False)
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

        most_similar = avg_sim[0:15]

        if len(most_similar) > 0:
            avg_similarity = sum([item[1] for item in most_similar]) / len(most_similar)

        avg_similarities[n_neighbors] = avg_similarity

    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,6))
    plt.plot(list(avg_similarities.keys()), list(avg_similarities.values()))
    plt.xlabel('Number of Neighbors')
    plt.ylabel('Average Similarity')
    plt.title('Average Similarities vs Number of Neighbors')
    plt.show()

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

    most_similar = avg_sim[0:15]

    recommendations = []
    for i in range(len(most_similar)):
        row = najslicnijePjesme.iloc[most_similar[i][0]]
        song_name, song_album, song_artists = row['name'], row['album'], row['artists']
        artist_objects = [Artist(name=artist['name'], id=artist['id']) for artist in song_artists]
        recommendation = SuggestionModel(name=song_name, album=song_album, artists=artist_objects)
        recommendations.append(recommendation)

    return recommendations