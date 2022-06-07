FROM ubuntu:latest
COPY requirements.txt /requirements.txt
COPY setup.py /setup.py
COPY README.md /README.md
COPY geniusbot /geniusbot
RUN apt update
RUN apt upgrade -y
RUN apt install python3 python3-pip
RUN python3 -m pip install --upgrade pip