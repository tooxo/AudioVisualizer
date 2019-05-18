import AudioVisualizer as aw
import audioStream as a
import threading
from flask import Flask

def AudioVis():
    v = aw.AudioVisualizer()
    v.start()
try:
    threading.Thread(target=AudioVis).start()
    a.Server()
except KeyboardInterrupt as ke:
    print("Im done for real now.")
