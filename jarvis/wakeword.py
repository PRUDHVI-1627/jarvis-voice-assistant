import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model

SAMPLE_RATE = 16000
FRAME_SAMPLES = 1280  # openWakeWord wants audio in 80ms chunks, and 1280 samples at 16kHz = 80ms

# this downloads the small pretrained model files the first time it runs, then caches them
openwakeword.utils.download_models()
oww_model = Model()

def wait_for_wake_word(threshold=0.5, stop_event=None):
    print("(waiting for 'hey jarvis'...)")
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    stream.start()

    try:
        while True:
            if stop_event is not None and stop_event.is_set():
                return False

            frame, _ = stream.read(FRAME_SAMPLES)
            frame = frame.flatten()

            predictions = oww_model.predict(frame)

            for name, score in predictions.items():
                if "jarvis" in name.lower() and score > threshold:
                    return True
    finally:
        stream.stop()
        stream.close()