class Request:
    new_line = b'\r\n'
    doube_new_line = b'\r\n\r\n'

    def __init__(self, request: bytes):
        [request_line, headers_as_bytes, self.body] = split_request_data(request) # raw bytes
        [self.method, self.path, self.http_version] = parse_request_line(request_line) # string
        self.headers = parse_headers(headers_as_bytes) # dictionary: {string : string}
        
# return splited request data, each of which is raw byte
def split_request_data(request: bytes):
    firstNewLineIndex = request.find(Request.new_line)
    firstDoubleNewLineIndex = request.find(Request.doube_new_line)

    request_line = request[:firstNewLineIndex]
    header_as_bytes = request[firstNewLineIndex + len(Request.new_line) : firstDoubleNewLineIndex]
    body = request[firstDoubleNewLineIndex + len(Request.doube_new_line) :]
    return [request_line, header_as_bytes, body]
    
# return [method, path, http_version], each of which is string
def parse_request_line(request_line: bytes):
    return request_line.decode().split()

# return request's body as dictionary
def parse_headers(headers_as_bytes: bytes):
    list_of_headers = headers_as_bytes.decode().split(Request.new_line.decode())
    headerToValueDict = {}
    for item in list_of_headers:
        headerValList = item.split(":")
        header = headerValList[0].strip()
        value = headerValList[1].strip()
        headerToValueDict[header] = value
    return headerToValueDict


if __name__ == '__main__':
    sample_request = b'GET / HTTP/1.1\r\nHost: localhost:8000\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nsec-ch-ua-platform: "macOS"\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7\r\n\r\nI am body!'
    request = Request(sample_request)
    print(request.method)
    print(request.path)
    print(request.http_version)
    for item in request.headers.items():
        print(item)