# services/tts.py
from typing import Union, Iterable
from elevenlabs.client import ElevenLabs
from .PRIVATE_KEYS import ELEVENLABS_API_KEY

_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def synthesize_tts(
    text: str,
    *,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
) -> bytes:
    """
    Convert text to speech using ElevenLabs and return raw audio bytes.
    """
    audio: Union[bytes, bytearray, Iterable[bytes]] = _client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
    )
    if isinstance(audio, (bytes, bytearray)):
        return bytes(audio)
    return b"".join(audio)
