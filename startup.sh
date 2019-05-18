#!/bin/bash

# Startup Script #
cd /home/pi
amixer set Speaker 50%
amixer set Mic 50%
screen -S audio -d -m python3 ./AudioController.py > audio.log
screen -S update -d -m python3 ./updateCycler.py > update.log
echo "Startup Finished"
