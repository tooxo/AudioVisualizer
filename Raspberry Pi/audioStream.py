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
        @app.route('/off')
        def off():
            if os.path.exists("on.lock"):
                os.remove("on.lock")
            return Response("True")
        @app.route('/on')
        def on():
            f = open("on.lock","w+")
            f.close()
            return Response("True")
        @app.route('/status')
        def status():
            return Response(str(os.path.exists("on.lock")))
        @app.route('/masteron')
        def masteron():
            f = open("masteron.lock","w+")
            f.close()
            return Response("")
        @app.route('/masteroff')
        def masteroff():
            if os.path.exists("masteron.lock"):
                os.remove("on.lock")
            return Response("")
        @app.route('/masterstatus')
        def masterstatus():
            return Response(str(os.path.exists("masteron.lock")))
        app.run(host='0.0.0.0', port=8123, threaded=True, debug=True, use_reloader=False)
