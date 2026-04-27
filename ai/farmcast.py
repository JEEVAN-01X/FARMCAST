import os
import sys
from groq import Groq
from dotenv import load_dotenv
from diagnose import diagnose

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f),
            model="whisper-large-v3",
            language="kn",
            response_format="text"
        )
    return result.strip()

def extract_crop(text: str) -> str | None:
    crop_map = {
        "jowar": ["jowar", "ಜೋಳ", "jola"],
        "ragi":  ["ragi", "ರಾಗಿ", "raagi"],
        "tomato": ["tomato", "ಟೊಮೇಟೊ", "tamatar"],
        "cotton": ["cotton", "ಹತ್ತಿ", "hatti"],
        "groundnut": ["groundnut", "ಕಡಲೆಕಾಯಿ", "kadalekayi", "peanut"],
    }
    text_lower = text.lower()
    for crop, keywords in crop_map.items():
        if any(k in text_lower for k in keywords):
            return crop
    return None

def run(audio_path: str) -> dict:
    print(f"\n[1] Transcribing: {audio_path}")
    transcript = transcribe(audio_path)
    print(f"    Transcript: {transcript}")

    crop = extract_crop(transcript)
    print(f"[2] Detected crop: {crop or 'unknown'}")

    print(f"[3] Diagnosing...")
    result = diagnose(transcript, crop=crop)

    print(f"\n{'='*50}")
    print(f"STATUS  : {result['status']}")
    print(f"DISEASE : {result.get('disease', 'unknown')}")
    print(f"CROP    : {result.get('crop', crop or 'unknown')}")
    print(f"DIST    : {result.get('distance', 'N/A')}")
    print(f"\nRESPONSE:\n{result['response']}")
    print(f"{'='*50}\n")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No audio file given. Running text-mode tests...\n")
        tests = [
            ("my jowar plant has holes in stem and dead heart", "jowar"),
            ("tomato leaves curling upward thick yellow no fruit", "tomato"),
        ]
        for text, crop in tests:
            print(f"[TEST] crop={crop} | input={text}")
            r = diagnose(text, crop=crop)
            print(f"  disease={r.get('disease')} dist={r.get('distance')}")
            print(f"  {r['response'][:100]}\n")
    else:
        run(sys.argv[1])
