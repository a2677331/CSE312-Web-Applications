from re import A

start_loop = "{{loop}}"
end_loop = "{{end_loop}}"

class formPartBodyParser:
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
        # find header part from body
        endIndex = body.find(formPartBodyParser.doube_new_line)
        headerData = body[ : endIndex]
        # split each header line
        listOfHeaders = headerData.split(formPartBodyParser.new_line)
        emptyItem = listOfHeaders.pop(0) # don't the first empty item
        assert len(emptyItem) == 0, "First header List item is not empty, please check"

        headers = {} # {String: String}
        for headerLine in listOfHeaders:
                splits = headerLine.decode().split(":")
                header = splits[0].strip()
                value = splits[1].strip()
                headers[header] = value
        return headers
        
    def parseContent(self, body: bytes):
        startIndex = body.find(formPartBodyParser.doube_new_line)
        assert startIndex != -1, "The request does not contain body content"
        contentData = body[startIndex + len(formPartBodyParser.doube_new_line) : ]
        return contentData.rstrip(b'\r\n') # dont't want after each comment content
    
    def parseContentDispositionOf(self, name: str, body: bytes):
        headers = self.parseHeader(body)
        contentDisposition = headers["Content-Disposition"]
        startingIndex = contentDisposition.find(name + "=\"")
        valueOfName = contentDisposition[startingIndex+len(name + "=\""):]
        endingIndex = valueOfName.find("\";")
        valueOfName = valueOfName[:endingIndex]
        return valueOfName

def splitFormBodyAsList(headers, body): # -> list of form part bodys
    boundaryBytes = getBoundary(headers).encode()
    splits = body.split(boundaryBytes)
    assertAns = "Body content splits number: " + str(len(splits)) +  ", please check your form body"
    assert len(splits) == 5, assertAns
    bodySplits = splits[1:-1]   # don't want first empty part and last part that contains part of last boundary
    return bodySplits # [comment part, image part]

# return loop placeholder with rendered loop content -> String
def renderLoop(loop_template, path, comment):
    loop_template = loop_template.replace("{{image_path}}", "\"" + path + "\"" + "class=\"my_image\"") # replace with "image path"
    loop_template = loop_template.replace("{{comment}}", comment) # replace with comment
    loop_template = loop_template.lstrip(start_loop) # remove {{loop}}
    loop_template = loop_template.rstrip(end_loop)   # remove {{end_loop}}
    return loop_template

def renderPlaceholder(placeholder: str, value: str,filename: str):
    with open(filename, 'r') as f:
        content = f.read()
        return content.replace(placeholder, value)

# for the whole loop content including {{loop}} and {{end_loop}}
def extractLoop(filename, prefix, suffix): 
    with open(filename, "r") as f:
        content = f.read()
        startIndex = content.find(prefix)
        endIndex = content.find(suffix)
        return content[startIndex:endIndex+len(suffix)] # -> String

# return {var} from www.example.com/prefix/{var}
def getStringAfter(prefix, path):
    startIndex = path.find(prefix)
    return path[startIndex + len(prefix):]
    
def getBoundary(headers): # -> String
    contentType = headers["Content-Type"]
    startIndex = contentType.find("multipart/form-data; boundary=")
    return "--" + contentType[startIndex + len("multipart/form-data; boundary=") : ]
    

# testData = readBytes("template.html")
# template_loop = extractLoop("template.html", "{{loop}}", "{{end_loop}}")    # get loop template from template.html
# print("template_loop now is: ")
# print(template_loop)
# renderLoop = renderLoop(template_loop, "cat", "12312312")
# print("rendered loop: ")
# print(renderLoop)
 