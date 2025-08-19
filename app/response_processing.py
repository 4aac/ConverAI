from user_speech_processing import text_processing, speech_to_text

from PRIVATE_KEYS import OPENAI_API_KEY
from openai import OpenAI

from PRIVATE_KEYS import ELEVENLABS_API_KEY
from elevenlabs.client import ElevenLabs
from elevenlabs import play


def response(context: str) -> str:
    """
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an English speaking practice assistant."},
            {"role": "user", "content": context}
        ]
    )
    return chat_response.choices[0].message.content


def vocal_response() -> None:
    """
    """
    elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
    )

    audio = elevenlabs.text_to_speech.convert(
        text=response(text_processing(speech_to_text())),
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    play(audio)


