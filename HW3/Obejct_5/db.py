from bson import json_util
import os
from pymongo import MongoClient

# Setup database connection
def get_database(collection: str):
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    # for local mongo DB
    # CONNECTION_STRING = "mongodb://localhost:27017" 
    
    # for docker container
    CONNECTION_STRING = "mongo"

    # Create a connection using MongoClient
    mongo_client = MongoClient(CONNECTION_STRING) # create instance
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
        ID_collection.insert_one({"id": 0})    # create id with 0
    assert ID_collection.count_documents({}) == 1, "ID is either empty or more than 1"
    return ID_collection.find_one({})["id"]

# retrieve all records from database
def getAllRecords(collection):
    records = [] # a list of all record dicts
    for record in collection.find({}, {"_id": False}):
        records.append(record)
    return json_util.dumps(records) # return as json object

# Read filename by and output bytes
def readBytes(filename):
    assert os.path.exists(filename) == True, "The file: " + filename + " does not exist."
    with open(filename, 'rb') as f:
        print("Reading file: " + filename)
        return f.read()
    
def writeBytes(filename, content):
    if os.path.exists(filename):
        print("The file: " + filename + " already exist, overwriting...")

    with open(filename, "wb") as f:
        print("Writing file " + filename)
        return f.write(content)






# text = "OMG!"
# storeToFile("comments.txt", text)
# boundary = "e68a0877353c411b8972ec5f868b2e41"