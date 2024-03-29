import socketserver
import sys
import json
from tkinter import X
from bson import json_util
from request import Request, getParsedRequest
from response import generate_response
from database import generateNextID, getAllRecords, get_database, readBytes, writeBytes
from parsers import formPartBodyParser, formWholeBodyParser, getStringAfter, renderLoop, extractLoop
from security import escapeInput
import re
    

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    
    total_length = 0 # total length of a large data
    buffer = b""     # current buffer data 

    def handle(self):
        # Get request data
        received_data = self.request.recv(1024) # read data from TCP socket
        parsedRequest = getParsedRequest(received_data)
        
        # Handle buffer
        self.handleBuffer(parsedRequest)

        # Handle request
        response = self.handleRequest(parsedRequest)

        # Send out response through HTTP
        self.sendFile(response)
        print("Response sent.\n")
        
    def handleBuffer(self, parsedRequest):
        # initialize total content body length and initialize buffer with request body 
        if parsedRequest.method == "POST" and "Content-Length" in parsedRequest.headers and self.total_length == 0:
            self.total_length = int(parsedRequest.headers["Content-Length"])
            self.buffer = parsedRequest.body
        
        # check if total data length is received
        while len(self.buffer) < self.total_length:
            self.buffer += self.request.recv(1024) # keep reading data from TCP socket
    
        # After received all data, now assigning the complete body to request
        if self.buffer != b"" and self.total_length != 0:
            parsedRequest.body = self.buffer # update completed request body data

        # restore buffer to original state
        self.restoreBuffer()

    def sendFile(self, response):
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
        self.request.sendall(response)  # send completed response through HTTP

    def restoreBuffer(self):
        # restore buffer to original state
        self.total_length = 0 # for entering the while loop
        self.buffer = b""
        
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
        
        response = generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Not Found: parseGET Method </h1>")
        
        # for image requests
        # for video requests
        # for audio requests
        # for html requests
        # for js requests
        # for css requests

        if path == "/" or path == "/index.html":
            response = generate_response(b"200 OK", b"text/html; charset=utf-8", readBytes("index.html"))
        elif path == "/style.css":
            response = generate_response(b"200 OK", b"text/css; charset=utf-8", readBytes("style.css"))
        elif path == "/functions.js":
            response = generate_response(b"200 OK", b"text/javascript; charset=utf-8", readBytes("functions.js"))
        elif re.search("/image/(.)+(jpg)$", path):
            imageName = getStringAfter("/image/", path)
            imageName = imageName.replace("/", "") # "/" in image name NOT allowed in the file path
            response = generate_response(b"200 OK", b"image/jpeg", readBytes("image/" + imageName))
        elif path == "/users":                           # Retrieve all records
            allRecords = getAllRecords(chat_collection)
            response = generate_response(b"200 OK", b"application/json", allRecords.encode())
        elif re.search("/users/[0-9]+", path): # to retriece single record from path "/users/{id}": /users/1...
            # Assume that all {id} are well-formed integers.
            userID = int(getStringAfter("/users/", path))                     # get the record id from path
            record = chat_collection.find_one({"id": userID}, {"_id": False}) # find single record according to userID
            
            if record: # find single record according to id
                response = generate_response(b"200 OK", b"application/json", json_util.dumps(record).encode())
                
        return response

    # Parse POST request and create proper response
    def parsePOST(self, path, headers, body):
        
        response = generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Not Found: parsePOST Method </h1>")
        
        # Parse creating single user in "/users" path
        if path == "/users" and headers["Content-Type"] == "application/json": # if "/users" path and json type, then add a user with new id
            bodyObj = json.loads(body.decode())                                # convert json into python obj
            bodyObj["id"] = generateNextID(userID_collection)                  # assign an ID for the new user
            chat_collection.insert_one(bodyObj)                                # create records in database
            createdRecord = chat_collection.find_one(bodyObj, {"_id": False})  # get created record but don't show "_id"
            jsonBody = json_util.dumps(createdRecord)                       
            response = generate_response(b"201 Created", b"application/json", jsonBody.encode())

        # Parse multi-part form upload in "/image-upload" path
        elif path == "/image-upload" and "multipart/form-data" in headers["Content-Type"]: # if to submit multipart form, then parse form data
            # Parse out imageName and comment parts from multipart form
            formBodyList = formWholeBodyParser(headers, body)         # parse multi-part form's body into a list
            commentPart = formPartBodyParser(formBodyList[0])         # first part of the form is comment
            escapedComment = escapeInput(commentPart.content)         # Security: escape user submissions of "&", "<" and ">"
            imagePart = formPartBodyParser(formBodyList[1])           # second part of the form is image

            # Save {image name: comment} dict to db, and save actual image file on server
            imageName = "image/image" + str(generateNextID(imageID_collection)) + ".jpg"  # generate image path name
            image_comment_collection.insert_one({ imageName: escapedComment.decode() })   # store image_name to comment dict to db
            writeBytes(imageName, imagePart.content)                                      # store actual image file on server disk

            # Load imageName_to_comment dict from db
            list_of_dicts = json.loads(getAllRecords(image_comment_collection))           # get all records from database
            template_loop = extractLoop("template.html", "{{loop}}", "{{end_loop}}")      # get loop template from template.html
            rendered_loop = "" # rendered loop to replace the template loop
            for image_to_comment_dict in list_of_dicts:  # replace loop template with all {path: comment} pairs
                for imagePath, comment in image_to_comment_dict.items():
                    rendered_loop += renderLoop(template_loop, imagePath, comment) # add up rendered loops
                    rendered_loop += "<hr>" # for horizontal line between each image

            # Render template file with newly rendered HTML content
            templateBytes = readBytes("template.html")
            renderedBytes = templateBytes.replace(template_loop.encode(), rendered_loop.encode())
            writeBytes("index.html", renderedBytes)                                # replace index.html with new render template
            response = generate_response(b"301 Moved Permanently", b" ", b" ", b"/")
         
        return response


if __name__ == "__main__":

    # Setup database connection
    userID_collection = get_database("userID")               # create "userID" collection
    chat_collection = get_database("chat")                   # create "chatCollection" collection
    imageID_collection = get_database("imageID")             # create "imageID" collection
    image_comment_collection = get_database("image_comment") # create "imageID" collection
    
    # image_comment_collection.delete_many({})
    # imageID_collection.delete_many({})

    print("Server's data:")
    print(json.loads(getAllRecords(image_comment_collection)))

    # Setup Server connection
    HOST, PORT = "0.0.0.0", 8000
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    sys.stdout.flush() # needed to use combine with docker
    sys.stderr.flush() # whatever you have buffer, print it out to the screen
    server.serve_forever()




# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port
# ps -fA | grep python

# # for test
# image_comment_collection.delete_many({})
# imageID_collection.delete_many({})