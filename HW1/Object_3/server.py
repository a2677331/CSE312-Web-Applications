import socketserver
import sys

def readByteData(filename):
    with open(filename, 'rb') as f:
        return f.read()

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = [] # if you want some data persist through all connections, use it

    def handle(self): 
    # while True: # means connection is established
        received_data = self.request.recv(1024)
        client_id = self.client_address[0] + ":" + str(self.client_address[1]) # 127.0.0.1:65413
        print("Client: " + client_id + " is requesting data")                  # 127.0.0.1:65413 is sending data:
        
        # Split HTTP request data
        HTTP_request_string = received_data.decode()            # get decoded HTTP request string data
        request_list = HTTP_request_string.split("\r\n")        # split HTTP request into array by new line symbol
        request_line = request_list[0].split(" ")               # HTTP request line such as: [GET, /, HTTP/1.1]
        self.parseRequest(request_line[0], request_line[1])     # parse HTTP request line and send out through HTTP
        
        # Cleanup and flusing
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen
    
    # Contruct Response according to requested MIME type and file name
    def parseRequest(self, request, path):
        path = path.lower() # case insensitive
        if request.upper() == "GET":
            if path == "/" or path == "/index.html":
                self.makeResponse200("text/html; charset=utf-8", readByteData("index.html"))
            elif path == "/style.css":
                self.makeResponse200("text/css", readByteData("style.css"))
            elif path == "/functions.js":
                self.makeResponse200("text/javascript", readByteData("functions.js"))
            elif "/image/" in path:
                imageFileName = self.getImageFileName(path)
                extension = imageFileName.split(".")[1]
                assert extension == "jpg", "*** File format not supported, the file must be a JPEG image ***"
                self.makeResponse200("image/jpeg", readByteData("image/" + imageFileName))
            else:
                self.notFound()

    # Parse image request
    def getImageFileName(self, path):
        imageName = path.split("/image/")[1]
        return imageName

    # Construct 200 status response and send out thorught HTTP
    def makeResponse200(self, MIMEType, byteData):
        status = "HTTP/1.1 200 OK"
        MIMEType = "\r\nContent-Type: " + MIMEType
        noSniff = "\r\nX-Content-Type-Options: nosniff"
        contentLength = "\r\nContent-Length: " + str(len(byteData))
        encoded_response = (status + MIMEType + noSniff + contentLength + "\r\n\r\n").encode() + byteData
        self.request.sendall(encoded_response)      # send constructed response throught HTTP

    # Construct 404 status response and send out thorught HTTP
    def notFound(self):
        encoded_response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 28\r\n\r\nSorry, page cannot be found!".encode()
        self.request.sendall(encoded_response)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8080
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler )
    server.serve_forever()


# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port