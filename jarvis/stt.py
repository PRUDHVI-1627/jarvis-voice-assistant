import tempfile

import numpy as np
import sounddevice as sd
import whisper
from scipy.io.wavfile import write as write_wav

SAMPLE_RATE = 16000

model = whisper.load_model("base")

def record_audio(duration=5):
    print(f"listening for {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write_wav(temp_file.name, SAMPLE_RATE, audio)
    temp_file.close()

    return temp_file.name

def transcribe(file_path):
    result = model.transcribe(file_path)
    return result["text"].strip()

def listen(duration=5):
    path = record_audio(duration)
    return transcribe(path)