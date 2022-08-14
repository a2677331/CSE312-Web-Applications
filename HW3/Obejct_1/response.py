from asyncore import write
from db import writeBytes

# Construct 200 status response and send out thorught HTTP
def generate_response(status: bytes, mimeType = b"text/plain", respBody=b"", location=b""):
    response = b"HTTP/1.1 " + status
    
    # for 101 Switching protocols
    if b"101" in status:
        response += b"\r\nUpgrade: " + respBody           # use respbody as upgrade header
        response += b"\r\nConnection: " + mimeType          # use mimeType as connection header
        response += b"\r\nSec-WebSocket-Accept: " + location + b"\r\n\r\n" # use location as sec_websockey_accept header, must have "\r\n\r\n" even without a body
        
    # for 204 No Content and 403 Forbidden
    elif b"204" in status or b"403" in status:
        return response + b"\r\n\r\n"                            # must have "\r\n\r\n" even without a body

    # for 301 Moved Permanently
    elif b"301" in status: 
        response += (b"\r\nLocation: " + location) + b"\r\n\r\n" # must have "\r\n\r\n" even without a body
        
    # for 200 OK, 201 Created, 404 Not Found
    else:                 
        response += b"\r\nContent-Type: " + mimeType
        response += b"\r\nContent-Length: " + str(len(respBody)).encode()
        if mimeType == b"image/jpeg":
            response += (b"\r\nX-Content-Type-Options: nosniff")  # only add if "image/jpeg" type
        response += b"\r\n\r\n" + respBody

    return response # raw bytes

    
