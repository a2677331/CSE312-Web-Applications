from re import I

from uuid import uuid4

def renderPlaceholder(placeholder: str, value: str,filename: str):
    with open(filename, 'r') as f:
        content = f.read()
        return content.replace(placeholder, value)
    
    
    

xsrf_token = str(uuid4())
addedTokenPage = renderPlaceholder("{{token}}", xsrf_token, "index.html")
print("Adding token into page...")
print(addedTokenPage)