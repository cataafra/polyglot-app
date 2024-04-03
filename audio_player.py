import pyaudio
import wave


def list_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']}")
    p.terminate()


def get_vb_audio_device():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(i, p.get_device_info_by_index(i))
        dev = p.get_device_info_by_index(i)
        if "CABLE Input" in dev['name']:
            return i
    p.terminate()
    return None


def play_audio(wav_path, output_device=None):
    print("Playing audio...")
    chunk = 1024
    wf = wave.open(wav_path, 'rb')
    p = pyaudio.PyAudio()

    if output_device is None:
        list_devices()
        return

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=output_device)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Audio playback complete.")