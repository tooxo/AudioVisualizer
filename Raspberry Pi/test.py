import pyaudio
from flask import Flask, Response
import audioop
import threading

app = Flask(__name__)

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')# (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')# (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')# (4byte) File type
    o += bytes("fmt ",'ascii')# (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')# (4byte) Length of above format data
    o += (1).to_bytes(2,'little')# (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')# (2byte)
    o += (sampleRate).to_bytes(4,'little')# (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')# (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')# (2byte)
    o += (bitsPerSample).to_bytes(2,'little')# (2byte)
    o += bytes("data",'ascii')# (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')# (4byte) Data size in bytes
    return o

def analyze(da):
     print(audioop.rms(da, 2))

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,input=True,channels=2,rate=44100,frames_per_buffer=1024)
header = genHeader(44100, 16, 2)

def test2():
    print("START")
    yield (header)
    while True:
        test = stream.read(512)
        yield (test)
        analyze(test)

@app.route('/')
def test():
    return Response(test2())

threading.Thread(target=test2).start()
app.run(host='0.0.0.0', port=8123, threaded=True, debug=True)
