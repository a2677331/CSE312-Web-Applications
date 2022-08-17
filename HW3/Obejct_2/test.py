
# # string = "jwijiirigjrigjri"
# # ord('X')                # 'X' has binary value 88 in the default encoding 
# # chr(88)                 # 88 stands for character 'X'
# # chr(0xc4)               # 0xC4 and 0xE8 are accented characters outside ASCII's range
# # for ch in string:
# #     unicode_number = ord(ch) # format take int, not char
# #     print( format(unicode_number, '08b') ) # print leading 0s up to 8, binary
# #     # print( format(unicode_number, '010b') ) # print leading 0s up to 10, binary

# # convert from raw bytes to binary
# from re import A
# import json


# Binary to bytes
encoded = b'\x81\xac\x93L\xfc\xe5\xe8n'
bits = ""

# from binary encoded to string
def binary_to_str(encoded):
    c = ""
    for code in encoded:
        c += format(code, '08b')  # or this merthod
    return c


# from bit string to byte string
def bitstring_to_bytes(bits: str):
    return int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder='big')

    


# binary_to_decimal = int("10001000", 2)
# print( binary_to_decimal )   
# raw_bytes = b"awijiirigjrigjri"
# print("a's Unicode number: ", raw_bytes[0])
# print("a's Hex number: ", hex(raw_bytes[0]))
# print("a's Binary number: ", bin(raw_bytes[0]))
# print("From Hex to Binary number: ", bin(0xc4), end="\r\n\r\n")

def print_binary(raw_bytes: bytes):
    count = 0
    for unicode_code in raw_bytes:
        count += 1
        print( format(unicode_code, '08b'), end=" ") # print leading 0s up to 8, binary
        if count % 4 == 0:
            print()


# print()
# s = "X"
# y = "Y"
# z = "Z"
# X = "XYZ"
# print(s.encode('utf-16')) # always 2 or 4 bytes per character, plus a BOM header
# print(y.encode('utf-16'))
# print(z.encode('utf-16'))
# print(X.encode('utf-16'))

# print(s.encode('utf-8'))
# print(y.encode('utf-8'))

# # leading 1s means the number of bytes for the character
# # 'Ä': 11000011(c3) 10000100(84) -> has 2 leading 1s, so is 2 bytes character

# B = 'Ä'           # b'\xc3\x84'       -> 2 bytes character
# print(B.encode())
# # print(b'\x81'.decode('utf-8'))  # decode using ascii characters, cannot decode other speical characters.

# hexstr = ""
# # "{0:08b}".format(int(XYZ, 16))
# print(bin(8))
# print(bin(1))





# # How to convert binary string into UTF-8 characters
# test_string = "1110001010011001101000000010000001110011011100000110000101100100011001010111001100001010111000101001100110100101001000000110100001100101011000010111001001110100011100110000101011100010100110011010011000100000011001000110100101100001011011010110111101101110011001000111001100001010111000101001100110100011001000000110001101101100011101010110001001110011"

# byte_string = test_string.encode("utf-8")

# int_string = int(test_string, 2) # binary to decimal
# print(int_string)

# hex_string = hex(int_string) # decimal to hex
# print(hex_string) # 0x7b226d65737361676554797065223a22636861744d657373616765222c22636f6d6d656e74223a22736e76227d

# chars = bytes.fromhex(hex_string.lstrip("0x")).decode('utf-8') # hex to chars
# print(chars)
# print(bytes.fromhex(hex_string.lstrip("0x")))


# # convert bytes of length to bits
# def get_length_bits_from(data_length: int):
#     if data_length < 126:
#         return bin(data_length)[2:].zfill(7)
#     elif 126 <= data_length and data_length < 65536:
#         return bin(126)[2:].zfill(7) + " OMG "+ bin(data_length)[2:].zfill(16)
#     else:
#         return bin(127)[2:].zfill(7) + " OMG " + bin(data_length)[2:].zfill(64)

# print(get_length_bits_from(126))
# print(get_length_bits_from(12423))

# print(get_length_bits_from(92423))
# print(get_length_bits_from(192423))



# print(bin(129).encode())

# # print(bin(int("0000000001111110")).encode())
# ff = "0000000001111110".encode()

# print(ff)


# print(b'10000001' == b'10000001')



# x = '01111011001000100110110101100101011100110111001101100001011001110110010101010100011110010111000001100101001000100011101000100010011000110110100001100001011101000100110101100101011100110111001101100001011001110110010100100010001011000010001001100011011011110110110101101101011001010110111001110100001000100011101000100010011001000110011001100001011001100010001001111101'


# # # Convert binary string into UTF-8 characters
# # def binary_to_str(bits: str):
# #     int_string = int(bits, 2)    # binary to decimal
# #     hex_string = hex(int_string) # decimal to hex

# #     print("Bits: ", bits)
# #     print("Int string:", int_string)
# #     print("Hex string: ", hex_string)

# #     return bytes.fromhex(x.lstrip("0x")).decode("utf-8") # hex to chars string

# # print(binary_to_str(x))


# t = "01111011001000100110110101100101011100110111001101100001011001110110010101010100011110010111000001100101001000100011101000100010011000110110100001100001011101000100110101100101011100110111001101100001011001110110010100100010001011000010001001100011011011110110110101101101011001010110111001110100001000100011101000100010011001000110011001100001011001100010001001111101"

# print(int(t,2))


# print(bitstring_to_bytes(t))

# bytesStr = bitstring_to_bytes(t)

# print(json.loads(bytesStr))
# print(type(json.loads(bytesStr)))


# n = b'\x81~\x00\xde[{"messageType": "chatMessage", "comment": "adfv", "username": "User219"}, {"messageType": "chatMessage", "comment": "gv", "username": "User548"}, {"messageType": "chatMessage", "comment": "hahaha", "username": "User213"}]'

# print(n)

# print(hex(b'\x81~\x00\xde[{"messageType": "chatMessage", "comment": "adfv", "username": "User219"}, {"messageType": "chatMessage", "comment": "gv", "username": "User548"}, {"messageType": "chatMessage", "comment": "hahaha", "username": "User213"}]'))

import json
from webscoket_utli import get_websocket_accept, websocketParser, get_length_bits_from, bitstring_to_bytes, binary_to_string

fake_payload = {"messageType": "chatMessage", "comment": "Super bug", "username": "HACKED"} # fake data

fake_payload_dict = [{"messageType": "chatMessage", "comment": "S", "username": "H"},
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"}, 
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"},
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"},
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"},
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"},
                {"messageType": "chatMessage", "comment": "S2", "username": "H2"}]

# encodedPayload = json.dumps(fake_payload_dict).encode()
# first_8_bits = bin(129).lstrip("0b").zfill(8)                    # first 8 bits of the socket frame, or close 10001000==136
# second_8_bits = "0" +  get_length_bits_from(len(encodedPayload))
# websocket_frame_bytes = bitstring_to_bytes(first_8_bits + second_8_bits) + encodedPayload

# print(" \n---------- ************** Sending websocket frame: ---------- ************** ")
# print("FIRST_8_BIT = ", first_8_bits)
# print("SECOND_8_BIT = ", second_8_bits)
# print("Payload is: ", encodedPayload)
# print("Payload length: ", len(encodedPayload))
# print("Encoded Frame: ", websocket_frame_bytes, "\n")
# print("FRAME in binary string: ") 
# print_binary(websocket_frame_bytes)
# print(" ---------- ************** End of Sending websocket frame ---------- ************** ")

# parsed_frame = websocketParser(websocket_frame_bytes)


jsonObj =  json.dumps(fake_payload)   # each payload is a JSON dict

pyObj = json.loads(jsonObj)

print(pyObj['comment'])

print(pyObj)