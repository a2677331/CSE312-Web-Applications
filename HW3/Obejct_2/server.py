import socketserver
import sys
import json
from bson import json_util
from request import Request, getParsedRequest
from response import generate_response
from db import generateNextID, getAllRecords, get_database, readBytes, writeBytes
from parsers import formPartBodyParser, getStringAfter, renderLoop, extractLoop, renderPlaceholder, splitFormBodyAsList
from security import escapeInput
import re
from uuid import uuid4
from webscoket_utli import get_websocket_accept, websocketParser, get_length_bits_from, bitstring_to_bytes, is_close_frame, print_binary
import random

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):

    # TODO need to send to all clients...
    clients = []     # TODO send to all clients in here
    response = None  # response from server
    total_length = 0 # total length of a large data
    buffer = b""     # current buffer data

    def handle(self):
        # Get request data
        received_data = self.request.recv(1024) # read data from TCP socket

        parsedRequest = getParsedRequest(received_data)

        # Handle buffer
        self.handleBuffer(parsedRequest)
        
        # Handle request
        self.response = self.handleRequest(parsedRequest)


        # Send out response through HTTP
        self.sendFile(self.response)
        
        # Handle websocket request
        if b"101 Switching Protocols" in self.response: # Check if the sent response is a successful websocket handshake
            print("YES, Switching Protocols is in response!")
            self.handleWebSocketRequest()
    

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
        
        
    def handleWebSocketRequest(self):

        # Starting websocket connection
        while True:
            print(" \n---------- ************** Receiving websocket frame: ---------- ************** ")
            received_data = self.request.recv(1024) # read data from TCP socket
            
            if len(received_data) != 0:
                # Parse the received data as websocket format
                payload_data = websocketParser(received_data) # Parse websocket request

                # Is is to close websocket request? 
                if is_close_frame(payload_data.bits):
                    return
                
                # Parse received data as WebSocket frame
                print_binary(received_data)
                jsonObj = payload_data.payload_bytes.decode() # decode as JSON obj
                py_dict =  json.loads(jsonObj)                # each payload is a JSON dict
                print("\n ---------- ************** End of Receiving websocket frame ---------- ************** ")
                
                py_dict["username"] = "User" + str(random.randint(0, 1000))  # add username to message
                py_dict["comment"] = escapeInput(py_dict["comment"])         # escaped user comment
                user_messages_collection.insert_one(py_dict)                 # insert into database
                del py_dict["_id"]                                           # don't want _id added from mongoDB

                self.sendFrame(py_dict)
                
   # Send a websocket frame from payload
    def sendFrame(self, payload_dict):
        encoded_payload = json.dumps(payload_dict).encode()  # encoded payload from dict
        first_8_bits = bin(129).lstrip("0b").zfill(8)        # first 8 bits, if need to close the websocket, use bin(136) 
        second_8_bits = "0" +  get_length_bits_from(len(encoded_payload)) # second 8 bits
        websocket_frame_bytes = bitstring_to_bytes(first_8_bits + second_8_bits) + encoded_payload
        self.sendFile(websocket_frame_bytes)                 # send data to client if there's one
        
        print(" \n---------- ************** Sending websocket frame: ---------- ************** ")
        print("FIRST_8_BIT = ", first_8_bits)
        print("SECOND_8_BIT = ", second_8_bits)
        print("Payload is: ", encoded_payload)
        print("Payload length: ", len(encoded_payload))
        print("Encoded Frame: ", websocket_frame_bytes, "\n")
        print("FRAME in binary string: ") 
        print_binary(websocket_frame_bytes)
        print(" ---------- ************** End of Sending websocket frame ---------- ************** ")
    
    # Parse HTTP request data and return HTTP response
    def handleRequest(self, request):
        if request.method == "GET":
            finalResponse = self.parseGET(request)
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
            return generate_response(b"200 OK", b"application/json", json.dumps(newRecord).encode())

    # Parse GET request and create proper response
    def parseGET(self, request: Request):
        
        response = generate_response(b"404 Not Found", b"text/html; charset=utf-8", b"<h1>404 Not Found: parseGET Method </h1>")

        # for home requests
        if request.path == "/" or request.path == "/index.html":
            # generate token for each page load
            xsrf_token = str(uuid4())
            token_collection.insert_one({"xsrf_token": xsrf_token}) # insert token for each page load
            addedTokenPage = renderPlaceholder("{{xsrf_token}}", xsrf_token, "index.html")
            response = generate_response(b"200 OK", b"text/html; charset=utf-8", addedTokenPage.encode())

        # for css requests
        elif request.path == "/style.css":
            response = generate_response(b"200 OK", b"text/css; charset=utf-8", readBytes("style.css"))

        # for js requests
        elif request.path == "/functions.js":
            response = generate_response(b"200 OK", b"text/javascript; charset=utf-8", readBytes("functions.js"))

        # for /image/{***.jpg} requests
        elif re.search("/image/(.)+(jpg)$", request.path):
            imageName = getStringAfter("/image/", request.path)
            imageName = imageName.replace("/", "") # "/" in image name NOT allowed in the file path
            response = generate_response(b"200 OK", b"image/jpeg", readBytes("image/" + imageName))

        # for /users requests
        elif request.path == "/users":                           # Retrieve all records
            allRecords = getAllRecords(chat_collection)
            response = generate_response(b"200 OK", b"application/json", allRecords.encode())

        # for /users/{id} requests
        elif re.search("/users/[0-9]+", request.path): # to retriece single record from path "/users/{id}": /users/1...
            userID = int(getStringAfter("/users/", request.path))             # get the id from path
            record = chat_collection.find_one( {"id":userID}, {"_id":False} ) # find single record according to userID
            # check if an user id exists
            if record: 
                response = generate_response(b"200 OK", b"application/json", json_util.dumps(record).encode())
        
        # for websocket upgrade requests
        elif request.path == "/websocket":
            # Get websocket headers for response
            connection = request.headers["Connection"]                     #  use for response header
            upgrade = request.headers["Upgrade"]                           #  use for response header
            
            # Generate websocket accept key
            sec_websocket_key = request.headers["Sec-WebSocket-Key"]       
            sec_websocket_accept = get_websocket_accept(sec_websocket_key) #  get websocket accept key from request key
            
            # Connection established generate 101 response code
            response = generate_response(b"101 Switching Protocols", connection.encode(), upgrade.encode(), sec_websocket_accept.encode())

        elif request.path == "/ws":
            # generate token for each page load
            response = generate_response(b"200 OK", b"text/html; charset=utf-8", readBytes("ws.html"))
        
        elif request.path == "/chat-history":
            allRecords = getAllRecords(user_messages_collection) 
            response = generate_response(b"200 OK", b"application/json", allRecords.encode())
                
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
            # Split the multipart form into list of bodies
            formBodySplits = splitFormBodyAsList(headers, body)
            
            # Security: check if valid token
            tokenBody = formBodySplits[0]                   # get token part of the form
            parsedTokenPart = formPartBodyParser(tokenBody) # parse the token body
            tokenString = parsedTokenPart.content.decode()  # token value is the body
            if token_collection.find_one({"xsrf_token": tokenString}) is None: # Return 403 response if not found
                return generate_response(b"403 Forbidden")

            # Parse out imageName and comment parts from multipart form
            commentBody = formBodySplits[1]   # get comment part of the form
            parsedCommentPart = formPartBodyParser(commentBody)             
            escapedCommentPart = escapeInput(parsedCommentPart.content.decode())                # Security: advoid HTML injection

            imageBody = formBodySplits[2]      # get image part of the form
            parsedImagePart = formPartBodyParser(imageBody)              

            # Save {image name: comment} dict to db, and save actual image file on server
            imageName = "image/image" + str(generateNextID(imageID_collection)) + ".jpg"  # generate image path name
            image_comment_collection.insert_one({ imageName: escapedCommentPart })   # store image_name to comment dict to db
            writeBytes(imageName, parsedImagePart.content)                                      # store actual image file on server disk

            # Load imageName_to_comment dict from db and generate {{loop}} html content
            list_of_dicts = json.loads(getAllRecords(image_comment_collection))           # get all records from database
            template_loop = extractLoop("template.html", "{{loop}}", "{{end_loop}}")      # get loop template from template.html
            rendered_loop = "" # rendered loop to replace the template loop
            for image_to_comment_dict in list_of_dicts:  # replace loop template with all {path: comment} pairs
                for imagePath, comment in image_to_comment_dict.items():
                    rendered_loop += renderLoop(template_loop, imagePath, comment) # add up rendered loops
                    rendered_loop += "<hr>" # for horizontal line between each image

            # Replace template html with rendered {{loop}} html content
            templateBytes = readBytes("template.html")
            renderedBytes = templateBytes.replace(template_loop.encode(), rendered_loop.encode())
            writeBytes("index.html", renderedBytes)  
            response = generate_response(b"301 Moved Permanently", b"", b"", b"/") # jump back to home page
         
        return response


if __name__ == "__main__":

    # Setup database connection
    userID_collection = get_database("userID")               # create "userID" collection
    chat_collection = get_database("chat")                   # create "chatCollection" collection
    imageID_collection = get_database("imageID")             # create "imageID" collection
    image_comment_collection = get_database("image_comment") # create "imageID" collection
    token_collection = get_database("token")                 # create "token" collection
    user_messages_collection = get_database("userMessages")  # create "userMessages" collection for WebSocket
    
    # image_comment_collection.delete_many({})
    # imageID_collection.delete_many({})
    # userID_collection.delete_many({})
    # chat_collection.delete_many({})
    # token_collection.delete_many({})
    # user_messages_collection.delete_many({})

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