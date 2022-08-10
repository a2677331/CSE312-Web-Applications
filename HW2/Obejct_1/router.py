from request import Request
from response import generate_response
import re
import json


def read_send_file(filename, MIME, reqeust, handler):
    with open(filename, "rb") as f:
        body = f.read()
        response = generate_response(body, MIME, "200 OK")
        handler.request.sendall(response)

# route's action functions
def four_oh_four(request: Request, handler):
    read_send_file("index.html", "text/html; charset=utf-8", request, handler)
def home(request, handler):
    read_send_file("index.html", "text/html; charset=utf-8", request, handler)
def js(request, handler):
    read_send_file("functinos.js", "text/javascript; charset=utf-8", request, handler)
def css(request, handler):
    read_send_file("style.css", "text/css; charset=utf-8", request, handler)
def images(request, handler):
    read_send_file("?????", "image/jpeg; charset=utf-8", request, handler) # ?????????

class Route:
    def __init__(self, method, filePath, action):
        self.method = method
        self.filePath = filePath
        self.action = action
    
    def is_request_match(self, request: Request):
        # if match HTTP method
        if self.method != request.method:
            return False
        # if match Path
        search_result = re.search('^' + self.filePath, request.path) # ^ means Starts with
        if search_result:
            return True
        else:
            return False
        
    def handleRequest(self, request: Request, handler):
        self.action(request, handler)
class Router:
    def __init__(self):
        self.routes = [] # alreayd stored valid routes
        self.route_404 = Route("", "", four_oh_four)

    def add_paths(self, route: Route):
        self.routes.append(route)
        print("Paths added: ", route.filePath)
    
    def handle_request(self, request: Request, handler):
        for route in self.routes:
            if route.is_request_match(request):
                route.handleRequest(request, handler) # ?????????
                return
        
        return self.route_404.handleRequest(request, handler)
                
def add_paths(router: Router):
    router.add_paths( Route("GET", "/functions.js", js) )
    router.add_paths( Route("GET", "/style.css", css) )
    router.add_paths( Route("GET", "/image/.", images) )
    router.add_paths( Route("GET", "/", home) )  

if __name__ == "__main__":
    sample_request = b'GET /happy HTTP/1.1\r\nHost: localhost:8000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nsec-ch-ua-platform: "macOS"\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7\r\n\r\nI am body!'
    request = Request(sample_request)
    
    router = Router()
    add_paths(router)
    


        
  

    

    
    
# def add_users_paths(router: Router):
#     router.add_paths( Route("POST", "/users", create) )
#     router.add_paths( Route("GET", "/users/.", retrieve) )
#     router.add_paths( Route("GET", "/users", list_all) )
#     router.add_paths( Route("PUT", "/users/.", update) )
#     router.add_paths( Route("DELETE", "/users/.", delete) )

# def create(request: Request, handler):
#     body_string = request.body.decode()
#     body_dict = json.loads(body_string)
#     body_dict['id'] = db.get_next_id()
#     db.create(body_dict)
#     response = generate_response("201 Created", 'application/json', json.dumps(body_dict).encode())
#     handler.request.sendall(response)

# def retrieve():
#     return
# def list_all():
#     return
# def update():
#     return
# def delete():
#     return

