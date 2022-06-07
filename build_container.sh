#!/bin/bash

docker build -t cryptobot:latest -f "./Dockerfile" .
docker run -v /mnt:/mnt -it cryptobot:latest bash
