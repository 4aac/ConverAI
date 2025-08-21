from typing import IO, Union
from werkzeug.datastructures import FileStorage
from openai import OpenAI
from .PRIVATE_KEYS import OPENAI_API_KEY
import re

_client = OpenAI(api_key=OPENAI_API_KEY)

def speech_to_text(
    file_like: Union[FileStorage, IO[bytes]], *,
    model: str = "whisper-1",
    language: str = "en",
    normalize: bool = False,
) -> str:
    """
    Transcribe an audio file-like object using OpenAI Whisper.

    Args:
        file_like: werkzeug FileStorage (Flask upload) or any binary IO handle.
        model: Whisper model name.
        language: Expected language code (e.g., "en").
        normalize: If True, remove punctuation from the resulting text.

    Returns:
        Transcribed text.
    """
    # Ensure the stream is positioned at the beginning
    stream = file_like
    if isinstance(file_like, FileStorage):
        stream = file_like.stream
        # Some file-like objects may lack a .name attribute; set a hint for the SDK
        if not getattr(stream, "name", None):
            stream.name = file_like.filename or "audio.webm"

    if hasattr(stream, "seek"):
        try:
            stream.seek(0)
        except Exception:
            pass

    text = _client.audio.transcriptions.create(
        model=model,
        file=stream,
        language=language,
        response_format="text",
    )

    if normalize:
        text = re.sub(r"[^\w\s]", "", text)

    return text
