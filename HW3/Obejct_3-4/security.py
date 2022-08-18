# -> str
def escapeInput(input: str):
    input = input.replace("&", "&amp;")
    input = input.replace("<", "&lt;")
    return input.replace(">", "&gt;")

