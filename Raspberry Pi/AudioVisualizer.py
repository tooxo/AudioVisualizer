#################################################################
####                                                         ####
#### CREATED WITH THE HELP OF user1405612 from stackoverflow ####
####                                                         ####
####         LINK TO HIS ORIGINAL THREAD ANSWER:             ####
####         https://stackoverflow.com/a/10669054            ####
#################################################################

import pyaudio
import os
import struct
import sys
import math
import time
import serial
import audioop
import numpy as np
import threading
import json as JSON
import subprocess
import signal

class AudioVisualizer():
    def __init__(self):
        self.INITIAL_TAP_THRESHOLD = 100
        self.FORMAT = pyaudio.paInt32
        self.SHORT_NORMALIZE = (1.0/32768.0)
        self.CHANNELS = 2
        self.RATE = 48000
        self.INPUT_BLOCK_TIME = 0.05
        self.sendtext = b"\x01"
        self.INPUT_FRAMES_PER_BLOCK = 1024

        self.OVERSENSITIVE = 15.0 / self.INPUT_BLOCK_TIME
        self.UNDERSENSITIVE = 120.0 / self.INPUT_BLOCK_TIME
        self.MAX_TAP_BLOCKS = 1200

        self.pa = pyaudio.PyAudio()

        self.tap_threshold = self.INITIAL_TAP_THRESHOLD
        self.noisycount = self.MAX_TAP_BLOCKS+1
        self.quietcount = 0
        self.errorcount = 0

        self.pro = None

        self.dict = dict()
        self.updateDict()

        self.arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print("###########################")
        print("")
        print("Initialized AudioVisualizer")
        print("")
        print("Using following Settings:")
        print(self.dict)
        print("")
        print("###########################")


    def get_rms(self, block):
        return(audioop.rms(block,2))

    def get_rms_manual(self, block):
        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )
        sum_squares = 0.0
        for sample in shorts:
            n = sample * self.SHORT_NORMALIZE
            sum_squares += n*n
        return math.sqrt( sum_squares / count )

    def arduinoPop(self):
        self.arduino.write(self.sendtext)

    def chromecastConnect(self):
        proc = ["/usr/bin/mkchromecast", "--alsa-device", "cloop", "--encoder-backend", "ffmpeg", "-n", self.dict["chromecastname"]]
        self.pro = subprocess.Popen(proc)

    def updateDict(self):
        file = open("save.json", "r")
        ret = JSON.loads(file.read())
        file.close()
        if self.dict != ret:
            self.dict = ret
            return True
        else:
            return False

    def callback(self,in_data,frame_count,time_info,status):
        amplitude = self.get_rms(in_data)
        #if status:
        #    print(status)
        ## used to remove buzzing noise from non-grounded audio jacks ##
        if self.dict["cutthreshold"] != 0:
            if bool(self.dict["auxout"]):
                array = np.fromstring(in_data, dtype=np.int32)
                if amplitude < self.dict["cutthreshold"]:
                    empty = np.zeros(len(array), dtype=np.int32)
                    return(empty, pyaudio.paContinue)
            else:
                if amplitude < self.dict["cutthreshold"]:
                    return(None, pyaudio.paContinue)
        # amplitude = self.get_rms_manual(in_data) #
        if amplitude > self.tap_threshold:
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > self.OVERSENSITIVE:
                self.tap_threshold *= 1.01
                print("DOWN",self.tap_threshold)
        else:
            if 1 <= self.noisycount <= self.MAX_TAP_BLOCKS:
                print("tap!",time.time(),amplitude)
                if bool(self.dict["lightson"]):
                    if (float(self.dict["delay"]) > 0):
                        secs = self.dict["delay"] / 1000
                        timer = threading.Timer(secs, self.arduinoPop, args=None, kwargs=None)
                        timer.start()
                    else:
                        self.arduinoPop()
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > self.UNDERSENSITIVE and self.tap_threshold > 65:
                self.tap_threshold *= 0.09
                print("Up",self.tap_threshold)
        if bool(self.dict["auxout"]):
            return(in_data, pyaudio.paContinue)
        else:
            return(None, pyaudio.paContinue)

    def start(self):
        try:
            stream = self.pa.open(
                format = self.FORMAT,
                channels = self.CHANNELS,
                rate = self.RATE,
                input = True,
                output = bool(self.dict["auxout"]),
                input_device_index = int(self.dict["inputdevice"]),
                output_device_index = int(self.dict["outputdevice"]),
                frames_per_buffer = self.INPUT_FRAMES_PER_BLOCK,
                stream_callback = self.callback)

            if self.dict["output_type"] == "Chromecast":
                threading.Thread(target=self.chromecastConnect).start()
            try:
                while True:
                    time.sleep(1)
                    if self.updateDict():
                        print("Restarting, because of updated settings.")
                        break
                print("CLOSING.")
                self.arduino.close()
                stream.stop_stream()
                stream.close()
                self.pa.terminate()
            except Exception:
                print("CLOSING.")
                self.arduino.close()
                stream.stop_stream()
                stream.close()
                self.pa.terminate()
                if self.dict["output_type"] == "Chromecast":
                    self.pro.send_signal(signal.SIGINT)
        except Exception as e:
            print(time.time(),e,self.dict["inputdevice"])
