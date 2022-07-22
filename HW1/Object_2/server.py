import socketserver
import sys

# MyTCPHandler is also a base handler inherited from BaseRequestHandler
class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = [] # if you want some data persist through all connections, use it

    def handle(self): 
    # while True: # means connection is established
        received_data = self.request.recv(1024)
        client_id = self.client_address[0] + ":" + str(self.client_address[1]) # 127.0.0.1:65413
        print("Client: " + client_id + " is requesting data")            # 127.0.0.1:65413 is sending data:
        
        # Prepare HTTP request data
        HTTP_request_string = received_data.decode()            # get decoded HTTP request
        request_list = HTTP_request_string.split("\r\n")    # split HTTP request into array by new line symbol
        request_line = request_list[0].split(" ")                   # HTTP request line: GET / HTTP/1.1
        
        if request_line[0] == "GET":
            if request_line[1] == "/" or request_line[1] == "/index.html":
                self.default()
            elif request_line[1] == "/hi":
                self.hi()
            elif request_line[1] == "/hello":
                self.hello()
            else:
                self.notFound()

        # cleanup and flusing
        sys.stdout.flush() # needed to use combine with docker
        sys.stderr.flush() # whatever you have buffer, print it out to the screen

    def default(self):
        self.request.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 8\r\n\r\nWelcome!".encode())
    
    def hello(self):
        self.request.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\n\r\nHello!".encode())
    
    def hi(self):
        self.request.sendall("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /hello".encode())
    
    def notFound(self):
        self.request.sendall("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 28\r\n\r\nSorry, page cannot be found!".encode())

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8080
    server = socketserver.ThreadingTCPServer( (HOST, PORT), MyTCPHandler )
    server.serve_forever()


# sudo lsof -i:5000          ---> find process using port 5000
# kill $PID                  ---> kill the process on that port
# kill -9 $PID               ---> to forcefully kill the port