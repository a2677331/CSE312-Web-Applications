import hashlib, base64
from re import A

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class websocketParser():

    to_close = 136  # 10001000
    to_connect = 129 # 10000001
    
    def __init__(self, raw_bytes: bytes):
        print("\n @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Parsing up coming frame: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")
        print_binary(raw_bytes)
        print("\n @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Make sure the info above is correct before parsing @@@@@@@@@@@@@@@@@@@@@@@@@@@@@ \n")
        
        self.frame_bits = getBitsFromBytes(raw_bytes) # Convert raw bytes string to binary string
        self.mask_flag, self.seven_bits = get_second_8_bits(self.frame_bits)
        self.mask_bits, self.masked_payload_bits = parse_second_8_bits(self.mask_flag, self.seven_bits, self.frame_bits)
        self.payload_bytes = get_payload_bytes(self.mask_bits, self.masked_payload_bits)


def is_close_frame(bits: str):
    first_8_bits = getBinaryFromNthBytes(bits, 1)
    if int(first_8_bits, 2) == websocketParser.to_close:
        return True
    else:
        return False

# Parse second 8 bits:
def get_second_8_bits(bits: str):
    second_8_bits = getBinaryFromNthBytes(bits, 2)
    print("Second_8_bits: ", second_8_bits)
    return second_8_bits[0], second_8_bits[1:8]             # 7 bits of payload length if payload_length_decimal < 126

def parse_second_8_bits(mask_flag: str, seven_bits: str, bits: str):
    payload_length_case = int(seven_bits, 2)    # from bits into decimal
    print("Payload length Case: ", payload_length_case)

    # See if need to update payload length and get corresponding mask bytes
    if payload_length_case < 126:
        payload_length_bits = seven_bits
        if mask_flag == "0": # check if have mask bits for sending frame
            start_index = 2
            mask_bits = None
        else:
            mask_bits = getBinaryFromNthBytes(bits, 3) + getBinaryFromNthBytes(bits, 4)
            mask_bits += getBinaryFromNthBytes(bits, 5) + getBinaryFromNthBytes(bits, 6)
            start_index = 6

    elif payload_length_case == 126:
        payload_length_bits = getBinaryFromNthBytes(bits, 3) + getBinaryFromNthBytes(bits, 4)
        if mask_flag == "0": # check if have mask bits for sending frame
            start_index = 4
            mask_bits = None
        else:
            mask_bits = getBinaryFromNthBytes(bits, 5) + getBinaryFromNthBytes(bits, 6)
            mask_bits += getBinaryFromNthBytes(bits, 7) + getBinaryFromNthBytes(bits, 8)
            start_index = 8

    else: # payload_length_decimal == 127
        if mask_flag == "0": # check if have mask bits for sending frame
            start_index = 10
            mask_bits = None
        else:
            payload_length_bits = getBinaryFromNthBytes(bits, 3) + getBinaryFromNthBytes(bits, 4)
            payload_length_bits += getBinaryFromNthBytes(bits, 5) + getBinaryFromNthBytes(bits, 6)
            payload_length_bits += getBinaryFromNthBytes(bits, 7) + getBinaryFromNthBytes(bits, 8)
            payload_length_bits += getBinaryFromNthBytes(bits, 9) + getBinaryFromNthBytes(bits, 10)
            mask_bits = getBinaryFromNthBytes(bits, 11) + getBinaryFromNthBytes(bits, 12)
            mask_bits += getBinaryFromNthBytes(bits, 13) + getBinaryFromNthBytes(bits, 14)
            start_index = 14
    
    payload_bytes_length = int(payload_length_bits, 2)                  # get payload lenth in decimal, bytes number
    masked_payload_bits = bits[start_index * 8 : start_index * 8 + payload_bytes_length * 8]    # get payload_length number of bytes from read bytes
    
    print("Mask bits: ", bitstring_to_bytes(mask_bits))
    print("payload_length", payload_bytes_length)
    print("masked_data_bits", bitstring_to_bytes(masked_payload_bits))

    return mask_bits, masked_payload_bits
   
   

def get_payload_bytes(mask_bits: str, masked_payload_bits: str):

    # this is the original data when no mask bits
    if mask_bits is None:
        print("No mask bits, Original payload: ", bitstring_to_bytes(masked_payload_bits))
        return masked_payload_bits
    else:
    # Unmask the payload data with mask
        index = 0
        payload_bits = ""
        mask_len = len(mask_bits)
        for bit in masked_payload_bits:
            payload_bits += str(int(bit) ^ int(mask_bits[index])) # unmask each masked payload bit 
            if index < mask_len - 1:                              # if use all 4 bytes mask, then go to the mask's start
                index += 1
            else:
                index = 0
     
    payload_bytes = bitstring_to_bytes(payload_bits) # convert bits to bytes
    print("Original payload: ", payload_bytes)
    return payload_bytes

# convert bytes of length to bits
def get_length_bits_from(data_length: int):
    if data_length < 126:
        return bin(data_length)[2:].zfill(7)
    elif 126 <= data_length and data_length < 65536:
        print("Generating payload length bits: ", bin(126)[2:].zfill(7), bin(data_length)[2:].zfill(16))
        return bin(126)[2:].zfill(7) + bin(data_length)[2:].zfill(16)
    else:
        return bin(127)[2:].zfill(7)  + bin(data_length)[2:].zfill(64)


# from binary encoded to string
def binary_to_string(encoded):
    c = ""
    for code in encoded:
        c += format(code, '08b')  # or this merthod
    return c

# from bit string to byte string
def bitstring_to_bytes(bits: str):
    if bits != None:
        return int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder='big')

# get binary representation in string from raw bytes string
def getBitsFromBytes(bytes_string):
    bits_string = ""
    for unicode_code in bytes_string:
        bits_string += format(unicode_code, "08b")
    return bits_string

# Below are for getting sec-socket-accept key:
def get_sha1_hash(websocket_key: str): # -> bytes
    to_hash = websocket_key + GUID     # -> String
    to_hash_bytes = to_hash.encode()   # -> bytes
    return hashlib.sha1(to_hash_bytes).digest() # should sha1 the bytes obejct, not the hex byte object(hexdijest)
    
def get_base64(sha1_hashed_bytes: bytes):       # -> bytes
    return base64.b64encode(sha1_hashed_bytes).decode("ascii") # headers only accept ASCII style bytes, so need base64 encoding

def get_websocket_accept(websocket_key: str):   # -> bytes
    hased_bytes = get_sha1_hash(websocket_key)  # -> bytes
    return get_base64(hased_bytes)              # -> str

def getBinaryFromNthBytes(binary_string: str, n: int):
    return binary_string[8*(n-1):8*n]


def print_binary(raw_bytes: bytes):
    if raw_bytes != None:
        count = 0
        for unicode_code in raw_bytes:
            count += 1
            print( format(unicode_code, '08b'), end=" ") # print leading 0s up to 8, binary
            if count % 4 == 0:
                print()

if __name__ == '__main__':
    bytes = b'\x81\xad\xe83\xff8\x93\x11\x92]\x9b@\x9e_\x8dg\x86H\x8d\x11\xc5\x1a\x8b[\x9eL\xa5V\x8cK\x89T\x9a\x1a\xc4\x11\x9cW\x85^\x9aV\x9c\x11\xc5\x1a\x89Q\x9c\x1a\x95'
        
    data = websocketParser(bytes)

    
    # 0000101: 7 bits
    # payload length is 5 bytes: 0000101
    # pay load length case: 5
    # Mask bits:                00010101 01110101 00001000 00101000 
    # Payload_bits:             01101110 01010111 01100111 01101010 01110010
    # Payload_bits unmasked:    01111011 00100010 01101111 01000010 01100111