from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define the favorite song attributes
favorite_song = {
    "explicit":0,
    "danceability":0.734000027179718,
    "energy":0.6370000243186951,
    "key":0.3636400103569031,
    "loudness":0.7089999914169312,
    "mode":0,
    "speechiness":0.458050012588501,
    "acousticness":0.046390000730752945,
    "instrumentalness":0.000019999999494757503,
    "liveness":0.11315999925136566,
    "valence":0.6480000019073486,
    "tempo":0.6988800168037415,
    "duration_ms":0.33647000789642334,
    "time_signature":1,
    "year":0.8913000226020813
}

# Define the recommended song attributes
recommended_song =  {
   "explicit":0.14285714285714285,
   "danceability":0.7057857130255017,
   "energy":0.6548571458884648,
   "key":0.41558786588055746,
   "loudness":0.6944007064614978,
   "mode":0.0,
   "speechiness":0.45107857244355337,
   "acousticness":0.046819286820079596,
   "instrumentalness":0.00004714285673149529,
   "liveness":0.1853642841534955,
   "valence":0.6720714271068573,
   "tempo":0.6453364342451096,
   "duration_ms":0.3533557142530169,
   "time_signature":1.0,
   "year":0.8680114330989974,
}



# Convert the dictionaries to lists
favorite_song_vector = list(favorite_song.values())
recommended_song_vector = list(recommended_song.values())

# Calculate the cosine similarity
cosine_sim = cosine_similarity([np.array(favorite_song_vector)], [np.array(recommended_song_vector)])

print("Cosine Similarity: ", cosine_sim[0][0])