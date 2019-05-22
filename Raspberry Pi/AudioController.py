import AudioVisualizer as aw
import audioStream as a
import threading
from flask import Flask
import time
import os
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

sstatus = 3
def arduinoOut():
    isOn = True
    while True:
        f = open("open.lock", "r")
        status = f.read()
        f.close()
        global sstatus
        if (status is "1"):
            if sstatus is 2 or sstatus is 3:
                ser.write(b'\x03')
            sstatus = 1
        if status is "2":
            if sstatus is 1:
                ser.write(b'\x02')
            sstatus = 2
        if status is "3":
            if sstatus is 1:
                ser.write(b'\x02')
            sstatus = 3
        time.sleep(1)

def AudioVis():
    while True:
        if sstatus is 3:
            v = aw.AudioVisualizer()
            v.start()
        time.sleep(1)
try:
    threading.Thread(target=AudioVis).start()
    threading.Thread(target=arduinoOut).start()
    a.Server()
except KeyboardInterrupt as ke:
    ser.close()
    print("Im done for real now.")
