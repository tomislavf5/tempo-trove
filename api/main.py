from typing import List
from pymongo import MongoClient
from fastapi import FastAPI, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Connect to the database
client=MongoClient()
client = MongoClient('localhost', port=27017, username="admin", password="password")
db = client["tempo-trove-db"]


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
class AutocompleteModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str =  Field(...)
    album: str =  Field(...)

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
    tracks = list(db.tracks.find({"name": {"$regex": search.lower(), "$options" :'i'}}, {"name": 1, "album": 1}).limit(10))
    print(tracks)
    return tracks
