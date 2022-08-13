# Construct 200 status response and send out thorught HTTP
def generate_response(status: bytes, mimeType: bytes, respBody=b"", location=b""):
    
    # for 204 No Content
    if len(mimeType) == 0 and len(respBody) == 0:     
        return b"HTTP/1.1 " + status + b"\r\nContent-Length: 0"

    # for 301 Moved Permanently, jump to another path in location
    response = b"HTTP/1.1 " + status
    if len(location) > 0: 
        response += (b"\r\nLocation: " + location)
        
    # for 200 OK, 201 Created, 404 Not Found
    else:                 
        response += b"\r\nContent-Type: " + mimeType
        response += b"\r\nContent-Length: " + str(len(respBody)).encode()
        if mimeType == b"image/jpeg":
            response += (b"\r\nX-Content-Type-Options: nosniff")  # only add if "image/jpeg" type
        response += b"\r\n\r\n" + respBody

    return response # raw bytes