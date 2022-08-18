# syntax=docker/dockerfile:1

# Created a Dockerfile containing the commands to build an image

FROM python:3.9

# Set the home directory to /root, optional
ENV HOME /root

# cd into the home directory
WORKDIR /root

# Copy all app files from your machine to the image, important
COPY . .

RUN pip3 install -r requirements.txt

# Allow port to be read from outside the container, by default ports are blocked
EXPOSE 8000

# Wait for loading database before any futher action 
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

# Run the app, CMD will execute when the container is ran
CMD /wait && python3 server.py