import os
import subprocess
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def speak_kannada(text: str, output_file="response.mp3"):
    translation = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": f"Translate this to Kannada language only. Return only the Kannada text, nothing else:\n\n{text}"
        }],
        max_tokens=200
    )
    
    kannada_text = translation.choices[0].message.content.strip()
    print("Kannada translation:", kannada_text)
    
    tts = gTTS(text=kannada_text, lang="kn", slow=False)
    tts.save(output_file)
    print(f"Audio saved: {output_file}")
    
    subprocess.run(["mpg123", output_file])

speak_kannada("This is stem borer disease. Spray chlorpyrifos immediately on the stem.")
