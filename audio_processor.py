import os

import numpy as np
import soundfile as sf
from datetime import datetime

from datasets import load_dataset
from transformers import AutoProcessor, SeamlessM4Tv2ForSpeechToSpeech
from audio_player import play_audio, get_vb_audio_device


class AudioProcessor:
    def __init__(self, device):
        self.device = device
        self.processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
        self.model = SeamlessM4Tv2ForSpeechToSpeech.from_pretrained("facebook/seamless-m4t-v2-large").to(device)

    def process_audio(self, wav_path):
        input_wav, samplerate = sf.read(wav_path)

        audio_inputs = self.processor(audios=input_wav, sampling_rate=samplerate, return_tensors="pt").to(self.device)
        audio_array_from_wav = self.model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()
        output_path = "processed_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav"

        sf.write(output_path, audio_array_from_wav, samplerate)

        print(f"Processed and saved as: {output_path}")
        os.remove(wav_path)
        play_audio(output_path, get_vb_audio_device())

    def process_audio_vad(self, audio_q):
        max_silence_allowed = 3000  # 3 seconds of allowed silence in milliseconds
        frame_duration = 30  # Duration of each audio frame in milliseconds
        current_segment = []
        speech_end_wait_time = 0

        while True:
            item = audio_q.get()
            if item is None:  # Signal to stop processing
                break
            data, is_speech = item

            if is_speech:
                current_segment.append(data)
                speech_end_wait_time = 0
            else:
                if current_segment:
                    speech_end_wait_time += frame_duration
                if speech_end_wait_time >= max_silence_allowed:
                    self._process_segment(current_segment)
                    current_segment = []
                    speech_end_wait_time = 0

        if current_segment:
            self._process_segment(current_segment)

    def _process_segment(self, segment):
        audio_segment = np.concatenate(segment, axis=0)
        wav_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav"
        sf.write(wav_path, audio_segment, 16000)
        self.process_audio(wav_path)
