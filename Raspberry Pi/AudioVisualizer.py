#################################################################
####                                                         ####
#### CREATED WITH THE HELP OF user1405612 from stackoverflow ####
####                                                         ####
####         LINK TO HIS ORIGINAL THREAD ANSWER:             ####
####         https://stackoverflow.com/a/10669054            ####
#################################################################

import pyaudio
import struct
import math
import time
import serial
import audioop

class AudioVisualizer():
    def __init__(self):
        self.INITIAL_TAP_THRESHOLD = 100
        self.FORMAT = pyaudio.paInt32
        self.SHORT_NORMALIZE = (1.0/32768.0)
        self.CHANNELS = 2
        self.RATE = 48000
        self.INPUT_BLOCK_TIME = 0.05
        self.sendtext = b"\x01"
        #self.INPUT_FRAMES_PER_BLOCK = int(self.RATE * self.INPUT_BLOCK_TIME)
        # TESTING W/ THE INPUT FRAMES PER BLOCK
        self.INPUT_FRAMES_PER_BLOCK = 1024

        self.OVERSENSITIVE = 15.0 / self.INPUT_BLOCK_TIME
        self.UNDERSENSITIVE = 120.0 / self.INPUT_BLOCK_TIME
        self.MAX_TAP_BLOCKS = 1200

        self.pa = pyaudio.PyAudio()

        self.tap_threshold = self.INITIAL_TAP_THRESHOLD
        self.noisycount = self.MAX_TAP_BLOCKS+1
        self.quietcount = 0
        self.errorcount = 0

        self.arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

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

    def callback(self,in_data,frame_count,time_info,status):
        amplitude = self.get_rms(in_data)
        if status:
            print(status)
        #amplitude = self.get_rms_manual(in_data)
        if amplitude > self.tap_threshold:
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > self.OVERSENSITIVE:
                self.tap_threshold *= 1.01
                print("DOWN",self.tap_threshold)
        else:
            if 1 <= self.noisycount <= self.MAX_TAP_BLOCKS:
                print("tap!",time.time(),amplitude)
                self.arduino.write(self.sendtext)
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > self.UNDERSENSITIVE:
                self.tap_threshold *= 0.09
                print("Up",self.tap_threshold)
        return(in_data, pyaudio.paContinue)

    def start(self):
        try:
            stream = self.pa.open(format = self.FORMAT,
                channels = self.CHANNELS,
                rate = self.RATE,
                input = True,
                output = True,
                frames_per_buffer = self.INPUT_FRAMES_PER_BLOCK,
                stream_callback = self.callback)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.arduino.close()
                stream.stop_stream()
                stream.close()
                self.pa.terminate()
        except Exception as e:
            print(time.time(),e)
