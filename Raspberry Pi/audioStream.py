from flask import Flask, Response, request
import pyaudio
import json as JSON
import os
import threading

class Server():
    def writeSettingsToDisk(self):
        file = open("save.json", "w")
        file.write(self.dict)
        file.close()

    def __init__(self):
        app = Flask(__name__)
        file = open("save.json", "r")
        self.dict = JSON.loads(file.read())
        file.close()
        @app.route('/devices',methods=['GET'])
        def devices():
            pp = pyaudio.PyAudio()
            info = pp.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            string = ""
            output = ""
            for i in range(0, numdevices):
                if (pp.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    string += "Input Device id " + str(i) + " - " + pp.get_device_info_by_host_api_device_index(0, i).get('name') + "\n"
                if (pp.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                    output += "Output Device id " + str(i) + " - " + pp.get_device_info_by_host_api_device_index(0, i).get('name') + "\n"
            return Response(string + "\n" + output)
        @app.route('/req_settings',methods=['GET'])
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

        @app.route('/status')
        def status():
            f = open("open.lock", "r")
            string = f.read()
            f.close()
            return Response(string)
        # 1 Everything off. 2 Lights only, no visu, 3 All
        @app.route('/setstatus',methods=["POST"])
        def setstatus():
            f = open("open.lock", "w+")
            string = request.data.decode()
            if string == "1" or string == "2" or string == "3":
                f.write(string)
                f.close()
                return Response("")
            else:
                return Response("Malformed Req.")
        app.run(host='0.0.0.0', port=8123, threaded=True, debug=True, use_reloader=False)
