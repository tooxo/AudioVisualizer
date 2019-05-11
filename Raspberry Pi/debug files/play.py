import pyaudio
import wave
import os

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

p = pyaudio.PyAudio()
output = p.open(format = FORMAT,
    channels = 1,
    rate = RATE,
    output = True)
with open('example.mp3', 'rb') as fh:
    while fh.tell() != os.path.getsize('example.mp3'):
    AUDIO_FRAME = fh.read(CHUNK_SIZE)
output.write(AUDIO_FRAME)
