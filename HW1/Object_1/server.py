import socketserver
import sys
import time


# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = [] # if you want some data persist through all connections, use it

        # get request body if exists, return None if no body content
    def getRequestBodyByLength(self, headerDict, request_body):
        if "Content-Length" in headerDict:
            return( request_body[:int(headerDict["Content-Length"])] )
        else:
            return None
            
    # get request header
    def getHeader(self, listOfHeader):
        headerDict = {} # HTTP header dictionary
        for header in listOfHeader:
            headerList = header.split(":")
            headerDict[ headerList[0].rstrip() ] = headerList[1].lstrip()
        return headerDict

    def getPath(self, method_path_ver, listOfHeader):
        protocol = "http"
        host = listOfHeader["Host"] 
        path = method_path_ver[1]
        port = 8080
        return protocol + "://" + host + ":" + str(port) + path

    # Setup resp status code
    resp_status = {"OK": "200", "MovePermanently": "301", "NotModified": "304", "Forbidden": "403", "NotFound": "404", "ServerError": "500"} 
    # response status code and meaning


    def handle(self): 

    # while True: # means connection is established
        received_data = self.request.recv(1024)

        # 127.0.0.1(host) : 51693(client port number)
        client_id = self.client_address[0] + ":" + str(self.client_address[1]) 
        print(client_id + " is sending data:") 
        print(len(received_data)) # length of client request content
        self.clients.append(client_id)
        print(self.clients)
        
        # Prepare HTTP request data
        HTTP_request = received_data.decode()  # get decoded HTTP request
        request_list = HTTP_request.split("\r\n\r\n")    # split by double new line signal
        request_but_body = request_list[0]  # un-parsed request data except body
        request_body = request_list[1]  # un-parsed request body 

        # Parse and get HTTP request line
        request_data_list = request_but_body.split("\r\n")   # split the request data by single new line signal
        method_path_ver = request_data_list[0].split(" ") # get the first request line list: [method, path, HTTPver]

        # Parse and get HTTP header key-value pairs
        del request_data_list[0]     # get rid of the first request line list, the rest is header string
        headerDict = self.getHeader(request_data_list) # parse and get the request header key-value pairs
        # Parse and get HTTP request body, if any
        body = self.getRequestBodyByLength(headerDict, request_body) # request body string of length specified by request header

        # Parse the requested path
        method = method_path_ver[0]
        path = method_path_ver[1]
        msg = "404 Not Found, sorry, page cannot be found!"
        status = "200" # default is 200 OK
        location = ""

        # Find status code
        if (method == "GET" and path == "/") or (method == "GET" and path == "/index.html"):
            msg = "Welcome to the homepage!"
        elif method == "GET" and path == "/hi": 
            status = self.resp_status["MovePermanently"] # Move Permanently: 301
            msg = "" # for Firefox compatibility
            location += "\r\nLocation: http://localhost:8080/hello" # redirect to /hello page
        elif method == "GET" and path == "/hello":
            msg = "Hello World!"
        else:
            status = self.resp_status["NotFound"]        # 404 Not Found

        # Construct server resp to client
        resp = "HTTP/1.1 " + status + "\r\nContent-Length: " + str(len(msg))
        resp += "\r\nContent-Type: text/plain; charset=utf-8"
        resp += location + "\r\n\r\n" + msg

        print("\n\n")
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
        self.request.sendall(resp.encode()) # Send data here!!



if __name__ == "__main__":
    host = "localhost"
    port = 8080

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever() 