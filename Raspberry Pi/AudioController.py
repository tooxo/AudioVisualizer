import AudioVisualizer as aw
import audioStream as a
import threading
from flask import Flask
import time

def AudioVis():
    while True:
        v = aw.AudioVisualizer()
        v.start()
        time.sleep(1)
try:
    threading.Thread(target=AudioVis).start()
    a.Server()
except KeyboardInterrupt as ke:
    print("Im done for real now.")
