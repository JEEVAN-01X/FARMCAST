import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(audio_file_path: str) -> str:
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language="kn"
        )
    return transcription.text

