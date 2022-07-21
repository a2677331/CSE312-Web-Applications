import socketserver
import sys

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = [] # if you want some data persist through all connections, use it

    # get request body if exists, return None if no body content
    def getRequestBodyByLength(self, headerDict, request_content):
        if "Content-Length" in headerDict:
            return( request_content[:int(headerDict["Content-Length"])] )
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
        client_id = self.client_address[0] + ":" + str(self.client_address[1]) # 127.0.0.1:65413
        print("Client: " + client_id + " is requesting data")            # 127.0.0.1:65413 is sending data:
        print("Data received length: " + str(len(received_data)) )            # length of client request content
        
        # Prepare HTTP request data
        HTTP_request = received_data.decode()            # get decoded HTTP request
        print("**************** Http Request: ****************")
        print(HTTP_request)
        print("***********************************************")
        request_list = HTTP_request.split("\r\n\r\n")    # split HTTP request into array by double new line symbol
        request_line = request_list[0]                   # HTTP request line: GET / HTTP/1.1
        request_body = request_list[1]                   # request body
        print("**************** HTTP request line ****************")
        print( str(request_line) )
        print("**************************************************")
        print("**************** HTTP request body ****************")
        print( str(request_body) )
        print("**************************************************")

        # Parse and get HTTP request line
        print("****************  Parsing HTTP request ****************")
        data_list = request_line.split("\r\n")        # split the request data by single new line symbol
        print("HTTP Data list: " + str(data_list) )

        # Parse and get HTTP header key-value pairs
        method_path_ver = data_list[0].split(" ")     # turn HTTP request line into: [method, path, HTTP ver]
        del data_list[0]     # get rid of the first request line list, the rest are all header pairs arrays
        headerDict = self.getHeader(data_list) # parse and get the request header key-value pairs
        print("HeaderDict: " + str(headerDict) )
        print("*******************************************************")

        # Parse and get HTTP request body, if any
        request_content = self.getRequestBodyByLength(headerDict, request_body) # request body string of length specified by request header

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

        print("Constructing HTTP Response...")
        print("HTTP requested path is: " + path)
        print("----------- HTTP response --------------")
        print(resp)
        print("----------------------------------------")
        self.request.sendall(resp.encode()) # Send data here!!



if __name__ == "__main__":
    host = "localhost"
    port = 8080
    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever() 