import AudioVisualizer as aw

try:
    while True:
        v = aw.AudioVisualizer()
        v.start()
except KeyboardInterrupt as ke:
    print("Im done for real now.")
