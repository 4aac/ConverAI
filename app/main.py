from user_speech_processing import speech_to_text, text_processing
from response_processing import response

def main():
    user = speech_to_text()
    user_processed = text_processing(user)
    answer = response(user_processed)
    return user_processed, answer

convo = main()
print(f"Asier: {convo[0]}")
print(f"AI: {convo[1]}")

