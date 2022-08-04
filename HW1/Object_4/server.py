import socketserver
import sys
from pymongo import MongoClient
import json
from bson import json_util

NEWLINE = "\r\n"
DOUBLE_NEWLINE = "\r\n\r\n"

# Setup MongoDB connection
try:
    mongo_client = MongoClient("mongo") # create instance
except:
    print("Could not connect to MongoDB")
db = mongo_client["cse312"]         # create database
chat_collection = db["chat"]        # create chat collection
userID_collection = db["userID"]            # create id collection

# Read filename by and output bytes
def readByteData(filename):
    with open(filename, 'rb') as f:
        return f.read()

# id increased by 1, or create an id starting with 0, updated id will be stored in database
def getNextID():
    filter = {"id": getID()}
    newValue = {"$inc": {"id": 1}}
    userID_collection.update_one(filter, newValue) # update id by one, or id is 0 if not exists
    return userID_collection.find_one({})["id"]

# Get User ID from id collection
def getID():
    # ⚠️ is .count_documents({}) NOT count_documents
    if userID_collection.count_documents({}) == 0: # if no id was found
        userID_collection.insert_one({"id": 0}) # create id with 0
    assert userID_collection.count_documents({}) == 1, "ID is either empty or more than 1"
    return userID_collection.find_one({})["id"]

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self): 
    # while True: # means connection is established
        received_data = self.request.recv(1024)
        if len(received_data) == 0:  # don't go further if empty data received
            return
        
        # Get decoded HTTP request data and check if it's empty
        decodedRequestData = received_data.decode()            # get decoded HTTP request string data
        print("\n______________Received HTTP Request___________________")
        print(decodedRequestData)
        print("_________________________________________________________")
    
        # Get method and path from decoded request data
        method, path = self.getMethodPath(decodedRequestData)

        # Parse HTTP request line and return HTTP response
        response = self.handleRequest(method, path, decodedRequestData)

        # Send out response through HTTP and cleanup
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
        self.request.sendall(response)  # send completed response through HTTP

    # get request method, path from request data
    def getMethodPath(self, requestData):
        firstNewLineIndex = requestData.find(NEWLINE)       # get the first new line character
        requestLine = requestData[:firstNewLineIndex]      # HTTP request line "GET / HTTP/1.1"
        requestLineList = requestLine.split()              # split request line by space
        return requestLineList[0], requestLineList[1]      # get request method, path
        
    # Parse HTTP request data and return HTTP response
    def handleRequest(self, method, path, requestData):
        if method == "GET":
            encodedResponse = self.parseGET(path)
        elif method == "POST":
            bodyObj = self.getRequestBody(requestData)   # convert json into python obj
            encodedResponse = self.parsePOST( bodyObj)   # Create encoded response
        elif method == "PUT":
            pathID = int(path.split("/users/")[1])       # get integer id from path: "users/{id}"
            bodyObj = self.getRequestBody(requestData)   # convert json into python obj
            encodedResponse = self.parsePUT(pathID, bodyObj)
        elif method == "DELETE":
            pathID = int(path.split("/users/")[1])       # get the record integer id from path
            encodedResponse = self.parseDELETE(pathID)
        else:
            encodedResponse = self.response404()

        return encodedResponse

    # Parse out the record body in a request
    def getRequestBody(sefl, requestData):
        firstDoubleNewLineIndex = requestData.find(DOUBLE_NEWLINE)     # get request body
        body = requestData[firstDoubleNewLineIndex + len(DOUBLE_NEWLINE) : ]
        print("HTTP request body length: " + str(len(body.encode())))  # needed to check if the request body is fully received
        return json.loads(body)                                        # convert json into python obj

    # Parse DELETE request and create proper response
    def parseDELETE(self, pathID):
        # Assume that all {id} are well-formed integers.
        result = chat_collection.delete_one({"id": pathID}) # delete record with id
        if result.deleted_count == 0: # number of deleted items
            return self.response404("The record with ID [" + pathID + "] was not found.")
        else:
            return self.response204()
    
    # Parse PUT request and create proper response
    def parsePUT(self, pathID, bodyObj): 
        result = chat_collection.find_one({"id": pathID}) # find record with {id} in the database
        # Update record's content from with found id, or return 404 page if can't find the record
        if result == None:
            return self.response404("404 Page Not Found: No record or the record has been deleted")
        else: 
            filter = {"id": pathID}
            newRecord = {"email": bodyObj["email"], "username": bodyObj["username"]}
            chat_collection.update_one(filter, {"$set": newRecord})             # update new record under pathID 
            updatedRecord = chat_collection.find_one(newRecord, {"_id": False}) # get updated record from database for response
            return self.response200("application/json", json_util.dumps(updatedRecord).encode())

    # Parse GET request and create proper response
    def parseGET(self, path):
        if path == "/" or path == "/index.html":
            return self.response200("text/html; charset=utf-8", readByteData("index.html"))
        elif path == "/style.css":
            return self.response200("text/css", readByteData("style.css"))
        elif path == "/functions.js":
            return self.response200("text/javascript", readByteData("functions.js"))
        elif "/image/" in path:
            return self.response200("image/jpeg", readByteData("image/" + self.getImageFileName(path)))
        elif path == "/users":     # Retrieve all records
            allRecords = self.getAllRecords()
            return self.response200("application/json", json_util.dumps(allRecords).encode())
        elif "/users/" in path: # to retriece single record from path "/users/{id}": /users/1...
            # Assume that all {id} are well-formed integers.
            record_id = int(path.split("/users/")[1])   # get the record id from path
            record = chat_collection.find_one({"id": record_id}, {"_id": False}) # find single record according to id
            if record == None:
                return self.response404("404 Page Not Found: No record in the database")
            else:
                return self.response200("application/json", json_util.dumps(record).encode())
        else:
            return self.response404() # unknown path, return 404 page

    # Parse POST request and create proper response
    def parsePOST(self, bodyObj):
        bodyObj["id"] = getNextID()                  # assign an ID for the new user
        chat_collection.insert_one(bodyObj)          # create records in database
        createdRecord = chat_collection.find_one(bodyObj, {"_id": False})    # get created record but don't show "_id"
        jsonBody = json_util.dumps(createdRecord)
        return self.response201("application/json", jsonBody.encode()) 

    def getAllRecords(self):
        records = [] # a list of all record dicts
        for record in chat_collection.find({}, {"_id": False}):
            records.append(record)
        print(records) # print all records
        return records

    # Parse image request
    def getImageFileName(self, path):
        imageName = path.split("/image/")[1]
        return imageName

    # Construct 200 status response and send out thorught HTTP
    def response200(self, MIMEType, byteData):
        status = "HTTP/1.1 200 OK"
        contentType = NEWLINE + "Content-Type: " + MIMEType
        contentLength = NEWLINE + "Content-Length: " + str(len(byteData))
        noSniff = NEWLINE + "X-Content-Type-Options: nosniff"
        return (status + contentType+ contentLength + noSniff  + DOUBLE_NEWLINE).encode() + byteData
    
    # Construct 201 status response and send out thorught HTTP
    def response201(self, MIMEType, byteData):
        status = "HTTP/1.1 201 Created"
        contentType = NEWLINE + "Content-Type: " + MIMEType
        contentLength = NEWLINE + "Content-Length: " + str(len(byteData))
        noSniff = NEWLINE + "X-Content-Type-Options: nosniff"
        return (status + contentType + contentLength + noSniff + DOUBLE_NEWLINE).encode() + byteData

    # Construct 404 status response and send out thorught HTTP
    def response404(self, errMsg="Sorry, page cannot be found!"):
        contentLength = NEWLINE + "Content-Length: " + str(len(errMsg.encode()))
        return ("HTTP/1.1 404 Not Found" + NEWLINE + "Content-Type: text/plain" + contentLength + DOUBLE_NEWLINE + errMsg).encode()
    
    def response204(self):
        return ("HTTP/1.1 204 No Content" + NEWLINE + "Content-Length: 0" + DOUBLE_NEWLINE).encode()



if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler )
    server.serve_forever()

# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port