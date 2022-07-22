# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR /root
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Allow port 5000 to be accessed 
# from outside the container
EXPOSE 5000

COPY . .

# CMD python3 server.py

CMD [ "python3", "server.py"]