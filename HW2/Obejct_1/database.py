# id increased by 1, or create an id starting with 0, updated id will be stored in database
def generateNextID(userID_collection):
    filter = {"id": getID(userID_collection)}
    newValue =  {"id": 1}
    userID_collection.update_one(filter, {"$inc": newValue}) # update id by one, or id is 0 if not exists
    return userID_collection.find_one({})["id"]

# Get User ID from id collection
def getID(userID_collection):
    # ⚠️ is .count_documents({}) NOT count_documents
    if userID_collection.count_documents({}) == 0: # if no id was found
        userID_collection.insert_one({"id": 0}) # create id with 0
    assert userID_collection.count_documents({}) == 1, "ID is either empty or more than 1"
    return userID_collection.find_one({})["id"]