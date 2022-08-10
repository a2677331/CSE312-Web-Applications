class formPartParser:
    
    # static variable for the Form class
    new_line = b'\r\n'
    doube_new_line = b'\r\n\r\n'
    
    # body: body content sperated by boundary from multipart Form, bytes format
    def __init__(self, body: bytes):
        self.headers = self.parseHeader(body)  # {String: String}
        self.content = self.parseContent(body) # bytes
        self.name = self.parseContentDispositionOf("name", body)         # from header content disposition
        self.filename = self.parseContentDispositionOf("filename", body) # from header content disposition
    
    def parseHeader(self, body: bytes):
        doubleNewLineIndex = body.find(formPartParser.doube_new_line)
        headerData = body[:doubleNewLineIndex]
        headerLineList = headerData.split(formPartParser.new_line)
        emptyItem = headerLineList.pop(0) # don't the first empty item
        assert len(emptyItem) == 0, "First header List item is not empty, please check"

        headers = {} # {String: String}
        for headerLine in headerLineList:
                splits = headerLine.decode().split(":")
                header = splits[0].strip()
                value = splits[1].strip()
                headers[header] = value

        return headers
        
    def parseContent(self, body: bytes):
        doubleNewLineIndex = body.find(formPartParser.doube_new_line)
        assert doubleNewLineIndex != -1, "The request does not contain body content"
        contentData = body[doubleNewLineIndex+len(formPartParser.doube_new_line):]
        return contentData
    
    def parseContentDispositionOf(self, name: str, body: bytes):
        headers = self.parseHeader(body)
        contentDisposition = headers["Content-Disposition"]
        startingIndex = contentDisposition.find(name + "=\"")
        valueOfName = contentDisposition[startingIndex+len(name + "=\""):]
        endingIndex = valueOfName.find("\";")
        valueOfName = valueOfName[:endingIndex]
        return valueOfName

def formBodyParser(headers, body):
    boundaryBytes = getBoundary(headers).encode()
    splits = body.split(boundaryBytes) 
    bodySplits = splits[1:-1]   # don't want first empty part and last part that contains part of last boundary
    return bodySplits

# return {var} from www.example.com/prefix/{var}, var contains no "/"
def pathParser(path, prefix):
    startingIndex = path.find(prefix)
    return path[startingIndex + len(prefix):].replace("/", "")
    
def getBoundary(headers): # -> String
    contentType = headers["Content-Type"]
    boundaryStartingIndex = contentType.find("boundary=") + len("boundary=")
    return "--" + contentType[boundaryStartingIndex:]
    
# # testData = b"Content-Disposition: form-data; name=\"upload\"; filename=\"discord.png\"\r\nContent-Type: application/octet-stream\r\n\r\nIMAGE_BYTES"
# # testData2 = b"Content-Disposition: form-data; name=\"comment\"\r\n\r\nCSE312 Sample Page This text is from the HTML file!\r\nThis text was added by JavaScript!"
# testData3 = b"------WebKitFormBoundaryApvL7J3Lyf8ABHPR\r\nContent-Disposition: form-data; name=\"comment\"\r\n\r\nzzzzzzzz\r\n------WebKitFormBoundaryApvL7J3Lyf8ABHPR\r\nContent-Disposition: form-data; name=\"upload\"; filename=\"\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\nWebKitFormBoundaryApvL7J3Lyf8ABHPR--"
# boundary = b"------WebKitFormBoundaryApvL7J3Lyf8ABHPR"
# form = Form(testData3)



        
        
 