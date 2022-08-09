import socketserver
import sys
from pymongo import MongoClient
import json
from bson import json_util
from request import Request 
from response import generate_response, readByteFrom, writeBytesTo
from database import generateNextID
from parseForm import Form, getBoundaryAsBytes
from security import escapeInput
from fileIO import storeToServer, loadFromServer

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self): 
        # Get request data
        received_data = self.request.recv(2048) # read data from TCP socket
        if len(received_data) == 0:              # don't go further if empty data received
            return
        
        # Print out request data for debugging 
        print("\n______________Received HTTP Request___________________")
        print(received_data.decode())
        print("_________________________________________________________")
    
        # Handle Request data and generate Response 
        request = Request(received_data) # parse request raw data
        response = self.handleRequest(request)

        # Send out response through HTTP and cleanup
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
        self.request.sendall(response)  # send completed response through HTTP

    # Parse HTTP request data and return HTTP response
    def handleRequest(self, request):
        if request.method == "GET":
            finalResponse = self.parseGET(request.path)
        elif request.method == "POST":
            finalResponse = self.parsePOST(request.path, request.headers, request.body)    # Create encoded response
        elif request.method == "PUT":
            bodyObj = json.loads(request.body.decode())          # convert json into python obj
            pathID = int(request.path.split("/users/")[1])       # get integer {id} from path: "users/{id}"
            finalResponse = self.parsePUT(pathID, bodyObj)
        elif request.method == "DELETE":
            pathID = int(request.path.split("/users/")[1])       # get integer {id} from path: "users/{id}"
            finalResponse = self.parseDELETE(pathID)
        else:
            finalResponse = generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>Sorry, unkonwn HTTP method(GET/POST/PUT/DELETE)!</h1>")

        return finalResponse

    # Parse DELETE request and create proper response
    def parseDELETE(self, pathID):
        # Assume that all {id} are well-formed integers.
        result = chat_collection.delete_one({"id": pathID}) # delete record with id
        if result.deleted_count == 0: # if didn't delete record 
            return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>The record with ID [" + pathID + "] was not found.</h1>")
        else: # deleted successfully
            return generate_response(b"204 No Content")
    
    # Parse PUT request and create proper response
    def parsePUT(self, pathID, bodyObj): 
        result = chat_collection.find_one({"id": pathID}) # find record with {id} in the database
        # Update record's content from with found id, or return 404 page if can't find the record
        if result == None:
            return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Page Not Found: No record or the record has been deleted</h1>")
        else: 
            filter = {"id": pathID}
            newRecord = {"email": bodyObj["email"], "username": bodyObj["username"]}
            result = chat_collection.update_one(filter, {"$set": newRecord})             # update new record under pathID 
            assert result.modified_count == 1, "Update failed, maybe record does not exist in the database?"
            return generate_response(b"200 OK", b"application/json", json.dumps(newRecord).encode())

    # Parse GET request and create proper response
    def parseGET(self, path):
        if path == "/":
            return generate_response(b"200 OK", b"text/html; charset=utf-8", readByteFrom("index.html"))
        elif path == "/index.html":
            return generate_response(b"200 OK", b"text/html; charset=utf-8", readByteFrom("index.html"))
        elif path == "/style.css":
            return generate_response(b"200 OK", b"text/css", readByteFrom("style.css"))
        elif path == "/functions.js":
            return generate_response(b"200 OK", b"text/javascript", readByteFrom("functions.js"))
        elif "/image/" in path:
            imageFile = "image/" + path.split("/image/")[1]
            return generate_response(b"200 OK", b"image/jpeg", readByteFrom(imageFile))
        elif path == "/users":     # Retrieve all records
            return generate_response(b"200 OK", b"application/json", self.getAllRecords().encode())
        elif "/users/" in path: # to retriece single record from path "/users/{id}": /users/1...
            # Assume that all {id} are well-formed integers.
            path_id = int(path.split("/users/")[1])   # get the record id from path
            record = chat_collection.find_one({"id": path_id}, {"_id": False}) # find single record according to id
            if record == None:
                return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>No record in the database</h1>")
            else:
                return generate_response(b"200 OK", b"application/json", json_util.dumps(record).encode())
        elif path == "/hi":
            return generate_response(b"200 OK", b"text/html; charset=utf-8", b"<h1>Hi there</h1>")

        return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>Sorry, page path cannot be found!</h1>")

    # Parse POST request and create proper response
    def parsePOST(self, path, headers, body):
        if path == "/users" and headers["Content-Type"] == "application/json": # if "/users" path and json type, then add a user with new id
            bodyObj = json.loads(body.decode())                            # convert json into python obj
            bodyObj["id"] = generateNextID(userID_collection)              # assign an ID for the new user
            chat_collection.insert_one(bodyObj)                            # create records in database
            createdRecord = chat_collection.find_one(bodyObj, {"_id": False})   # get created record but don't show "_id"
            jsonBody = json_util.dumps(createdRecord)                       
            return generate_response(b"201 Created", b"application/json", jsonBody.encode())

        elif path == "/image-upload" and "multipart/form-data" in headers["Content-Type"]: # if to submit multipart form, then parse form data
            boundary_as_bytes = getBoundaryAsBytes(headers)
            splits = body.split(boundary_as_bytes)
            bodySplits = splits[1:-1]   # don't want first empty part and last part that contains part of last boundary
            commentPart = Form(bodySplits[0])
            if commentPart.name == "comment":
                commentBytes = escapeInput(commentPart.content) # escape user submissions of "&", "<" and ">"
                storeToServer("comments.txt", commentBytes)        # store each comment into server

                # render template file with comments
                templateBytes = readByteFrom("template.html")
                loadedCommentBytes = loadFromServer("comments.txt").replace(b"\n", b"<br>") # replace all newline chars with html format
                replaced = templateBytes.replace(b"{{chats}}", loadedCommentBytes) # replace {{chats}} with loaded comments
                writeBytesTo("index.html", replaced)                               # replace index.html with new render template
                return generate_response(b"301 Moved Permanently", b" ", b" ", b"/")
            
        return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Not Found at parsePOST()</h1>")

    # retrieve all records from database
    def getAllRecords(self):
        records = [] # a list of all record dicts
        for record in chat_collection.find({}, {"_id": False}):
            records.append(record)
        print(records) # print all records
        return json_util.dumps(records) # return as json object

if __name__ == "__main__":
    # Setup database connection
    mongo_client = MongoClient("mongo") # create instance
    db = mongo_client["cse312"]         # create database
    chat_collection = db["chat"]        # create "chat" collection
    userID_collection = db["userID"]    # create "userID" collection

    # Setup Server connection
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler)
    server.serve_forever()

# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port