import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def to_english(text: str) -> str:
    """If text contains non-ASCII (Kannada), translate to English first."""
    if all(ord(c) < 128 for c in text):
        return text  # already English
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Translate this farmer's complaint to English. Return only the translation, nothing else:\n{text}"}],
        max_tokens=100,
        temperature=0
    )
    return response.choices[0].message.content.strip()
