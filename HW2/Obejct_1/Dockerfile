# syntax=docker/dockerfile:1

FROM python:3.9

ENV HOME /root
WORKDIR /root

COPY . .

RUN pip3 install -r requirements.txt

# Allow port 8080 to be accessed 
# from outside the container
EXPOSE 8000

# Wait for loading database before any futher action 
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 server.py