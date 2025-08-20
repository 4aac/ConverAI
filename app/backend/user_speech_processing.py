from PRIVATE_KEYS import OPENAI_API_KEY

import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI

import keyboard, pyaudio, wave

import re

FILE_NAME = "audio.wav"

def record_user_speech(frequency: int = 44100, channels: int = 1,
                       chunk: int = 2048) -> str:
    """
    """
    global FILE_NAME

    pa_format = pyaudio.paInt16
    pa = pyaudio.PyAudio()

    print("Press SPACE to start recording...")
    keyboard.wait("space")
    # Ensure the first press doesn't immediately stop recording
    while keyboard.is_pressed("space"):
        pass

    print("Recording... Press SPACE again to stop.")
    stream = pa.open(format=pa_format, channels=channels,
                     rate=frequency, input=True,
                     frames_per_buffer=chunk)

    frames = []
    try:
        while not keyboard.is_pressed("space"):
            # Prevent overflow errors on slower systems
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    with wave.open(FILE_NAME, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(pa.get_sample_size(pa_format))
        wf.setframerate(frequency)
        wf.writeframes(b"".join(frames))

    print("Stopped recording.")
    return FILE_NAME


def speech_to_text() -> str:
    """

    """
    global FILE_NAME

    client = OpenAI(api_key = OPENAI_API_KEY)

    # Safely open/close the recorded file
    with open(f"./{FILE_NAME}", "rb") as audio_file:
        # Transcribe recording into text
        transcription = client.audio.transcriptions.create(
            model = "whisper-1",
            file = audio_file,
            language = "en",
            response_format = "text"
        )

    # Normalize by removing punctuation (keep letters/numbers/spaces)
    normalized_transcription = re.sub(r"[^\w\s]", "", transcription)

    return normalized_transcription
