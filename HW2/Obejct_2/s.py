# Read filename by and output bytes
def readBytes(filename):
    with open(filename, 'rb') as f:
        return f.read()
    
def writeBytes(filename, content):
    with open(filename, "wb") as f:
        return f.write(content)

with open("body.txt", "rb") as f:
    content = f.read()
    splits = content.split(b"------WebKitFormBoundary5lpe1PLWnVai7OpL")
    print(len(splits))

    writeBytes("1.txt", splits[0])
    writeBytes("2.txt", splits[1])
    writeBytes("3.txt", splits[2])
    writeBytes("4.txt", splits[3])