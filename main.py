import queue
import threading
import torch

from audio_processor import AudioProcessor
from audio_recorder import AudioRecorder


def main():
    audio_q = queue.Queue()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    audio_processor = AudioProcessor(device)
    audio_recorder = AudioRecorder(audio_q, device)

    processing_thread = threading.Thread(target=audio_processor.process_audio_vad, args=(audio_q,), daemon=True)
    processing_thread.start()

    try:
        audio_recorder.record_audio_vad()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_q.put(None)
        processing_thread.join()


if __name__ == "__main__":
    main()
