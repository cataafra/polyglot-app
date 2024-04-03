import sounddevice as sd
import sys
import webrtcvad
import queue

class AudioRecorder:
    def __init__(self, audio_q, device, vad_aggressiveness=3, samplerate=16000, frame_duration=20, pause_threshold=500):
        self.audio_q = audio_q
        self.device = device
        self.vad_aggressiveness = vad_aggressiveness
        self.samplerate = samplerate
        self.frame_duration = frame_duration
        self.pause_threshold = pause_threshold

    def record_audio_vad(self):
        vad = webrtcvad.Vad(self.vad_aggressiveness)
        blocksize = int(self.samplerate * self.frame_duration / 1000)
        with sd.InputStream(callback=self._callback, device=None, channels=1, samplerate=self.samplerate, blocksize=blocksize, dtype='int16'):
            print("Recording... Press Ctrl+C to stop.")
            while True:
                sd.sleep(100)

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        is_speech = webrtcvad.Vad(self.vad_aggressiveness).is_speech(indata.tobytes(), self.samplerate)
        self.audio_q.put((indata.copy(), is_speech))
