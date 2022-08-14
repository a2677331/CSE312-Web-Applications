import hashlib, base64

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

sec_websocket_key = "dGhlIHNhbXBsZSBub25jZQ=="
sec_websocket_key_accept = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="
sec_websocket_key = "dGhlIHNhbXBsZSBub25jZQ=="
# sec_websocket_key = "BwmhKIOeQo5y3eSW5+TxwA=="

def get_sha1_hash(websocket_key: str): # -> bytes
    to_hash = websocket_key + GUID # -> String
    to_hash_bytes = to_hash.encode() # -> bytes
    return hashlib.sha1(to_hash_bytes).digest() # should sha1 the bytes obejct, not the hex byte object(hexdijest)
    
def get_base64(sha1_hashed_bytes: bytes):  # -> bytes
    return base64.b64encode(sha1_hashed_bytes).decode("ascii") # headers only accept ASCII style bytes, so need base64 encoding

def get_websocket_accept(websocket_key: str):   # -> bytes
    hased_bytes = get_sha1_hash(websocket_key)  # -> bytes
    return get_base64(hased_bytes)              # -> str
