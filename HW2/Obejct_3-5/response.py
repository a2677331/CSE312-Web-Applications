# Construct 200 status response and send out thorught HTTP
def generate_response(status: bytes, mimeType = b"text/plain", respBody=b"", location=b""):
    response = b"HTTP/1.1 " + status
        
    # for 204 No Content and 403 Forbidden
    if b"204" in status or b"403" in status:     
        return response
    
    # for 301 Moved Permanently
    if b"301" in status: 
        response += (b"\r\nLocation: " + location)
        
    # for 200 OK, 201 Created, 404 Not Found
    else:                 
        response += b"\r\nContent-Type: " + mimeType
        response += b"\r\nContent-Length: " + str(len(respBody)).encode()
        if mimeType == b"image/jpeg":
            response += (b"\r\nX-Content-Type-Options: nosniff")  # only add if "image/jpeg" type
        response += b"\r\n\r\n" + respBody

    return response # raw bytes

    
