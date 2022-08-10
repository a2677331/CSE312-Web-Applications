import os

def storeServer(filename, content): # (string, bytes) -> bytes
    exist = os.path.exists(filename)
    with open(filename, 'ab' if exist else 'wb') as f:
            f.write(content)

def loadServer(filename): # -> bytes
    assert os.path.exists(filename) == True, "The file: " + filename + " does not exist."
    with open(filename, 'rb') as f:
        return f.read()

# text = "OMG!"
# storeToFile("comments.txt", text)
# boundary = "e68a0877353c411b8972ec5f868b2e41"
