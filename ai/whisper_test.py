import os
from groq import Groq

# Load API key
client = Groq(api_key="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")  # paste your key here for now

# Transcribe audio
with open("test.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=audio_file,
        language="kn",  # Kannada
        response_format="text"
    )

print("Transcription:", transcription)