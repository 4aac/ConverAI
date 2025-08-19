from user_speech_processing import text_processing

from PRIVATE_KEYS import OPENAI_API_KEY
from openai import OpenAI

def response(context: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an English speaking practice assistant."},
            {"role": "user", "content": context}
        ]
    )
    return chat_response.choices[0].message.content
