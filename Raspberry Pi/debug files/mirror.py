import pyaudio
import time
WIDTH = 2
CHANNELS = 2
RATE = 48000
p = pyaudio.PyAudio()
def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)
stream = p.open(format = pyaudio.paInt32,
    channels = CHANNELS,
    rate = 48000,
    input = True,
    output = True,
    frames_per_buffer = 2400,
    stream_callback = callback)
stream.start_stream()
while stream.is_active():
    time.sleep(0.1)
stream.stop_stream()
stream.close()
p.terminate()
