from bson import json_util
import os
from pymongo import MongoClient

# Setup database connection
def get_database(collection: str):
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongo"
    CONNECTION_STRING2 = "mongodb+srv://a2677331:Aa089089@cluster0.fx2hgh6.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient
    mongo_client = MongoClient(CONNECTION_STRING2) # create instance
    db = mongo_client["CS312"]

    # Create the database
    return db[collection]

# id increased by 1, or create an id starting with 0, updated id will be stored in database
def generateNextID(ID_collection):
    filter = {"id": getID(ID_collection)}
    increasedValue =  {"id": 1}
    ID_collection.update_one(filter, {"$inc": increasedValue}) # update id by one, or id is 0 if not exists
    return ID_collection.find_one({})["id"]

# Get User ID from id collection
def getID(ID_collection):
    if ID_collection.count_documents({}) == 0: # if no id was found
        ID_collection.insert_one({"id": 0}) # create id with 0
    assert ID_collection.count_documents({}) == 1, "ID is either empty or more than 1"
    return ID_collection.find_one({})["id"]

# retrieve all records from database
def getAllRecords(collection):
    records = [] # a list of all record dicts
    for record in collection.find({}, {"_id": False}):
        records.append(record)
    return json_util.dumps(records) # return as json object

def store_bytes_server_append(filename, content): # (string, bytes) -> bytes
    exist = os.path.exists(filename)
    with open(filename, "wb" if not exist else "ab") as f:
            f.write(content)

def load_bytes_server(filename): # -> bytes
    assert os.path.exists(filename) == True, "The file: " + filename + " does not exist."
    with open(filename, 'rb') as f:
        return f.read()

# text = "OMG!"
# storeToFile("comments.txt", text)
# boundary = "e68a0877353c411b8972ec5f868b2e41"