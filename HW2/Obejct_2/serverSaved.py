import socketserver
import sys
from pymongo import MongoClient
import pymongo
import json
from bson import json_util
from request import Request
from response import generate_response, readBytes, writeBytes
from database import generateNextID, getAllRecords, store_bytes_server_append
from parsers import formPartBodyParser, formWholeBodyParser, pathParser, renderLoop, extractLoop
from security import escapeInput



    

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    
    total_length = 0 # for entering the while loop
    buffer = b""
    count = 0

    def handle(self):
        # Get request data
        received_data = self.request.recv(1024) # read data from TCP socket
        writeBytes("recvData_whole.txt", received_data)
        self.advoidEmptyRequest(received_data)
        parsedRequest = Request(received_data)
        
        # initialize total content body length and initialize buffer with request body 
        if parsedRequest.method == "POST" and "Content-Length" in parsedRequest.headers and self.total_length == 0:
            self.total_length = int(parsedRequest.headers["Content-Length"])
            self.buffer = parsedRequest.body
            writeBytes("first_buffer.txt", self.buffer)
            print("Initialized total length to and buffer")
        
        # check if total body length is still larger than total read body length
        while len(self.buffer) < self.total_length:
            print("Entered loop: ", len(self.buffer), " < ", self.total_length)

            # keep getting new buffer data and update
            self.buffer += self.request.recv(1024) # read data from TCP socket
            self.count += 1
    
        # After received all data, now assigning the complete body to request
        if self.buffer != b"" and self.total_length != 0:
            print("\nReceved Enough Data!\n")
            print("Adding To Buffer count: ", self.count)
            print("The whole form body stores to whole_buffer.txt")
            writeBytes("whole_buffer.txt", self.buffer)
            print("Read Body length now is: ", len(self.buffer))
            print("Total body length is now ", self.total_length)
            parsedRequest.body = self.buffer # update completed request body data

        response = self.handleRequest(parsedRequest)
        
        # restore buffer to original state
        self.restoreBuffer()

        # Send out response through HTTP
        self.sendFile(response)
        print("Response sent.")
        

    def advoidEmptyRequest(self, data: bytes):
        # don't go further if empty data received
        if len(data) == 0:             
            print("Received empty Request.")
            return

    def sendFile(self, response):
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
        self.request.sendall(response)  # send completed response through HTTP

    def restoreBuffer(self):
        # restore buffer to original state
        self.total_length = 0 # for entering the while loop
        self.buffer = b""
        self.count = 0
        
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
            return generate_response(b"200 OK", b"text/html; charset=utf-8", readBytes("index.html"))
        elif path == "/index.html":
            return generate_response(b"200 OK", b"text/html; charset=utf-8", readBytes("index.html"))
        elif path == "/style.css":
            return generate_response(b"200 OK", b"text/css; charset=utf-8", readBytes("style.css"))
        elif path == "/functions.js":
            return generate_response(b"200 OK", b"text/javascript; charset=utf-8", readBytes("functions.js"))
        elif "/image/" in path:
            imagePath = "image/" + pathParser(path, "/image/") # get the image path from path
            return generate_response(b"200 OK", b"image/jpeg", readBytes(imagePath))
        elif path == "/users":     # Retrieve all records
            allRecords = getAllRecords(chat_collection)
            return generate_response(b"200 OK", b"application/json", allRecords.encode())
        elif "/users/" in path: # to retriece single record from path "/users/{id}": /users/1...
            # Assume that all {id} are well-formed integers.
            userID = pathParser(path, "/users/")       # get the record id from path
            record = chat_collection.find_one({"id": int(userID)}, {"_id": False}) # find single record according to id
            if record == None:
                return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>No record in the database</h1>")
            else:
                return generate_response(b"200 OK", b"application/json", json_util.dumps(record).encode())

        return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>Sorry, page path cannot be found! GET Method </h1>")

    # Parse POST request and create proper response
    def parsePOST(self, path, headers, body):
        
        # Parse "/users" path
        if path == "/users" and headers["Content-Type"] == "application/json": # if "/users" path and json type, then add a user with new id
            bodyObj = json.loads(body.decode())                            # convert json into python obj
            bodyObj["id"] = generateNextID(userID_collection)              # assign an ID for the new user
            chat_collection.insert_one(bodyObj)                            # create records in database
            createdRecord = chat_collection.find_one(bodyObj, {"_id": False})   # get created record but don't show "_id"
            jsonBody = json_util.dumps(createdRecord)                       
            return generate_response(b"201 Created", b"application/json", jsonBody.encode())

        # Parse multi-part form
        elif path == "/image-upload" and "multipart/form-data" in headers["Content-Type"]: # if to submit multipart form, then parse form data

            # Parse out imageName and comment parts from multipart form
            formBodyList = formWholeBodyParser(headers, body)          # parse multi-part form's body into a list

            commentPart = formPartBodyParser(formBodyList[0])         # first part of the form is comment
            print("Comment part's name")
            print(commentPart.name)
            print("comment part's headers")
            print(commentPart.headers)
            print("comman part's content: ")
            print(commentPart.content)
            escapedComment = escapeInput(commentPart.content)     # Security: escape user submissions of "&", "<" and ">"

            imagePart = formPartBodyParser(formBodyList[1])           # second part of the form is image
            print("image part's name")
            print(imagePart.name)
            print("image part's headers")
            print(imagePart.headers)
            print("image part's filename: ")
            print(imagePart.filename)

            # Save image_to_comment dict to db, but actual image file on server
            imageName = "image" + str(generateNextID(imageID_collection)) + ".jpg"   # generate image name
            image_comment_collection.insert_one({ imageName: escapedComment.decode() }) # store image_name to comment dict to db
            
            print("Writing file to disk: ", imageName)
            store_bytes_server_append(imageName, imagePart.content)                        # store actual image file on server disk with new name ?????????????????????????????????????????????????????

            # Load imageName_to_comment dict from db
            list_of_dicts = json.loads(getAllRecords(image_comment_collection))         # get all records from database
            template_loop = extractLoop("template.html", "{{loop}}", "{{end_loop}}")    # get loop template from template.html
            rendered_loop = "" # rendered loop to replace the template loop
            for image_to_comment_dict in list_of_dicts:  # replace loop template with all {path: comment} pairs
                for path, comment in image_to_comment_dict.items():
                    rendered_loop += renderLoop(template_loop, path, comment) # add up rendered loops
            
            print("Rendered loop now is: ")
            print(rendered_loop)
            print()
            
            # Return rendered template file with new rendered loops 
            templateBytes = readBytes("template.html")
            renderedBytes = templateBytes.replace(template_loop.encode(), rendered_loop.encode())
            writeBytes("index.html", renderedBytes)                                # replace index.html with new render template
            return generate_response(b"301 Moved Permanently", b" ", b" ", b"/")
         
        return generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Not Found at parsePOST()</h1>")


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



if __name__ == "__main__":
    
    userID_collection = get_database("userID")       # create "userID" collection
    chat_collection = get_database("chat") # create "chatCollection" collection
    imageID_collection = get_database("imageID")     # create "imageID" collection
    image_comment_collection = get_database("image_comment")    # create "imageID" collection


    # # for test
    # image_comment_collection.delete_many({})
    # imageID_collection.delete_many({})
    
    
    print("Server's data:")
    dictObj = json.loads(getAllRecords(image_comment_collection))
    print(dictObj)




    # Setup Server connection
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler)
    server.serve_forever()

# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port
# ps -fA | grep python
# image_comment_collection.delete_many({})
# imageID_collection.delete_many({})