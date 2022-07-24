import socketserver
import sys
from pymongo import MongoClient
import json
from bson import json_util

# Setup MongoDB connection
mongo_client = MongoClient("mongo") # create instance
db = mongo_client["cse312"]         # create database
chat_collection = db["chat"]        # create collection

# Read filename by and output bytes
def readByteData(filename):
    with open(filename, 'rb') as f:
        return f.read()

# Get next User ID, incresed by 1
def getNextID():
    return chat_collection.count_documents({}) + 1

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = [] # if you want some data persist through all connections, use it

    def handle(self): 
    # while True: # means connection is established
        received_data = self.request.recv(1024)
        # client_id = self.client_address[0] + ":" + str(self.client_address[1]) # 127.0.0.1:65413
        # print("\nClient: " + client_id + " is requesting data")                  # 127.0.0.1:65413 is sending data:
        
        # Split HTTP request data
        requestData = received_data.decode()            # get decoded HTTP request string data
        print("\n______________Handling HTTP Request___________________")
        if "HTTP/1.1" not in requestData:
            print("            *** Empty request line ***")
            print("______________________________________________________")
            return
        else:
            print(requestData)
        print("______________________________________________________")
        requestList = requestData.split("\r\n")        # split HTTP request into array by new line symbol
        requestLine = requestList[0].split(" ")               # HTTP request line such as: [GET, /, HTTP/1.1]
        method, path = requestLine[0].upper(), requestLine[1].lower() # get request method, path

        # Parse HTTP request line and prepare HTTP response
        if method == "GET":
            encodedResponse = self.parseGET(path)     
        elif method == "POST":
            bodyObj = self.getRequestBody(requestData)   # convert json into python obj
            bodyObj["id"] = getNextID()                  # assign an ID for the new user
            chat_collection.insert_one(bodyObj)          # create records in database
            createdRecord = chat_collection.find_one(bodyObj, {"_id": False})      # show created record and don't show "_id"
            encodedResponse = self.parsePOST(path, json_util.dumps(createdRecord)) # Create encoded response
        elif method == "PUT":
            bodyObj = self.getRequestBody(requestData)    # convert json into python obj
            assert len(bodyObj) != 0, "Body content of PUT request should not be empty"
            encodedResponse = self.parsePUT(path, bodyObj)
        elif method == "DELETE":
            encodedResponse = self.parseDELETE(path)
        else:
            encodedResponse = self.response404()

        # Send out response through HTTP and cleanup
        print("\n-------------------- Response -----------------------------")
        print(encodedResponse.decode())
        print("----------------- End of Response -------------------------")
        self.request.sendall(encodedResponse)  # send completed response through HTTP
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen

    # Parse out the record body in a request
    def getRequestBody(sefl, requestData):
        # Parse out the record body that is in the POST request
        body = requestData.split("\r\n\r\n")[1]
        print("HTTP request body length: " + str(len(body.encode())))  # needed to check if the request body is fully received
        return json.loads(body)           # convert json into python obj

    # Parse DELETE request and create proper response
    def parseDELETE(self, path):
        # Assume that all {id} are well-formed integers.
        pathID = path.split("/users/")[1]                        # get the record id from path
        result = chat_collection.delete_one({"id": int(pathID)}) # delete record with id
        if result.deleted_count == 0: # number of deleted items
            return self.response404("The record with ID [" + pathID + "] was not found.")
        else:
            return self.response204()
    
    # Parse PUT request and create proper response
    def parsePUT(self, path, recordToFind): 
        if "/users/" in path: # to update single record from path "/users/{id}": /users/1... 
            # Find record according to attribute values
            record = chat_collection.find_one({"username": recordToFind["username"], "email": recordToFind["email"]})
            # Update record if found, or return 404 page if not found
            if record == None:  # no such record in database
                return self.response404("404 Page Not Found: No record or the record has been deleted")
            else:               # the record exists, update the record id with {id} from path
                # Assume that all {id} are well-formed integers.
                pathID = path.split("/users/")[1]    # get the record id from path
                chat_collection.update_one(record, {"$set": {"id": int(pathID)}})   # update record with new id
                # response 200 code and the updated record
                updatedRecord = chat_collection.find_one({"username": recordToFind["username"], "email": recordToFind["email"]}, {"_id": False})
                return self.response200("application/json", json_util.dumps(updatedRecord).encode())

        # unknown path, return 404 page
        return self.response404()

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
        elif path == "/users" or path == "/users/":     # Retrieve all records
            allRecords = self.getAllRecords()
            return self.response200("application/json", json_util.dumps(allRecords).encode())
        elif "/users/" in path: # to retriece single record from path "/users/{id}": /users/1...
            # Assume that all {id} are well-formed integers.
            record_id = int(path.split("/users/")[1])   # get the record id from path
            record = chat_collection.find_one({"id": record_id}, {"_id": False}) # find single record according to id
            if record == None:
                return self.response404("404 Page Not Found: No record in the database")
            else:
                print("Retreved Successfully")
                return self.response200("application/json", json_util.dumps(record).encode())

        # If statments above does not return successfully, then return 404(unknown path)
        return self.response404()

    # Parse POST request and create proper response
    def parsePOST(self, path, requestBody):
        if path == "/users" or path == "/users/":
            return self.response201("application/json", requestBody.encode()) 
        else: # unknown path, return 404
            return self.response404()

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
        contentType = "\r\nContent-Type: " + MIMEType
        contentLength = "\r\nContent-Length: " + str(len(byteData))
        noSniff = "\r\nX-Content-Type-Options: nosniff"
        return (status + contentType+ contentLength + noSniff  + "\r\n\r\n").encode() + byteData
    
    # Construct 201 status response and send out thorught HTTP
    def response201(self, MIMEType, byteData):
        status = "HTTP/1.1 201 Created"
        contentType = "\r\nContent-Type: " + MIMEType
        contentLength = "\r\nContent-Length: " + str(len(byteData))
        noSniff = "\r\nX-Content-Type-Options: nosniff"
        return (status + contentType + contentLength + noSniff + "\r\n\r\n").encode() + byteData

    # Construct 404 status response and send out thorught HTTP
    def response404(self, errMsg="Sorry, page cannot be found!"):
        contentLength = "\r\nContent-Length: " + str(len(errMsg.encode()))
        return ("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain" + contentLength + "\r\n\r\n" + errMsg).encode()
    
    def response204(self):
        return "HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n".encode()



if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler )
    server.serve_forever()


# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port