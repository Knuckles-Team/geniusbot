#!/bin/bash

docker build -t geniusbot:latest -f "./Dockerfile" .
docker run -v /mnt:/mnt -it geniusbot:latest bash
