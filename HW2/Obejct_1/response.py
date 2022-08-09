
# Construct 200 status response and send out thorught HTTP
def generate_response(status, MIMEType=b'', body=b'', location=b""):
    if len(MIMEType) == 0 and len(body) == 0:     # 204 No Content
        return b"HTTP/1.1 " + status + b"\r\nContent-Length: 0"
    else:
        response = b"HTTP/1.1 " + status  
        if len(location) > 0: # for 301 status
            response += (b"\r\nLocation: " + location) 
        else:                 #  for 200, 201, 404
            response += b"\r\nContent-Type: " + MIMEType
            response += b"\r\nContent-Length: " + str(len(body)).encode()
            response += b"\r\nX-Content-Type-Options: nosniff"
            response += b"\r\n\r\n" + body
        return response # raw bytes

# Read filename by and output bytes
def readByteFrom(filename):
    with open(filename, 'rb') as f:
        return f.read()
    
def writeBytesTo(filename, content):
    with open(filename, "wb") as f:
        return f.write(content)