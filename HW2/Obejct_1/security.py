# -> bytes
def escapeInput(input: bytes):
    input = input.replace(b"&", b"&amp;")
    input = input.replace(b"<", b"&lt;")
    return input.replace(b">", b"&gt;")

def cleanImagePathInjection(imagePath: str):
    imagePath.replace("/", "")