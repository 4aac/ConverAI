from PRIVATE_KEYS import OPENAI_API_KEY

import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI

import re


def record_user_speech(file_name: str, frequency: int = 44100, 
                       duration: int = 5,) -> str:
    """
    
    """
    # Start recorder with the given values 
    # of duration and sample frequency
    recording = sd.rec(int(duration * frequency), 
                    samplerate=frequency, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    file_name = file_name.replace(" ", "") + ".wav"

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write(file_name, frequency, recording)

    return file_name


def speech_to_text() -> str:
    """
    """
    client = OpenAI(api_key = OPENAI_API_KEY)
    
    file_name = record_user_speech("audio")
    audio_file = open(f"./{file_name}", "rb")

    # Transcribe recording into text
    transcription = client.audio.transcriptions.create(
        model = "whisper-1",
        file = audio_file,
        language = "en",
        response_format = "text"
    )
    return transcription


def text_processing(speech: str) -> str:
    """
    """
    clean_speech = speech.lower().strip()
    normalized_speech = re.sub(r"[^\w\s]", "", clean_speech)
    return normalized_speech

