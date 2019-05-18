from flask import Flask, Response, request
import pyaudio
import json as JSON
import os
import threading

class Server():
    def genHeader(self, sampleRate, bitsPerSample, channels):
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

    def writeSettingsToDisk(self):
        file = open("save.json", "w")
        file.write(self.dict)
        file.close()

    def __init__(self):
        pa = pyaudio.PyAudio()
        header = self.genHeader(44100, 16, 2)
        app = Flask(__name__)
        file = open("save.json", "r")
        self.dict = JSON.loads(file.read())
        file.close()
        #@app.route('/stream')
        #def audio():
        #    stream = pa.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=128)
        #    def gen(stream):
        #        yield (header + stream.read(128))
        #        while True:
        #            yield(stream.read(128))
        #    return Response(gen(stream))
        #@app.route('/')
        #def main():
        #    return Response(open("templates/index.html", 'r'))
        @app.route('/devices')
        def devices():
            pp = pyaudio.PyAudio()
            info = pp.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            string = ""
            output = ""
            for i in range(0, numdevices):
                if (pp.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    string = string + "Input Device id " + str(i) + " - " + pp.get_device_info_by_host_api_device_index(0, i).get('name') + "\n"
                if (pp.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                    output = output + "Output Device id " + str(i) + " - " + pp.get_device_info_by_host_api_device_index(0, i).get('name') + "\n"
            return Response(string + "\n" + output)
        @app.route('/req_settings')
        def req_settings():
            file = open("save.json", "r")
            self.dict = JSON.loads(file.read())
            return Response(str(self.dict))
        @app.route('/set_settings',methods=['POST'])
        def set_settings():
            try:
                self.dict = JSON.dumps(request.json)
                threading.Thread(target=self.writeSettingsToDisk).start()
                return Response("Done.")
            except Exception as e:
                return Response("Error." + str(e))
        app.run(host='0.0.0.0', port=8123, threaded=True, debug=True)
