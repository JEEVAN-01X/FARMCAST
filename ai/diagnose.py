import os
from groq import Groq
from dotenv import load_dotenv
from disease_db import query_disease, build_db

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UNKNOWN_THRESHOLD = 1.2

def to_english(text: str) -> str:
    if all(ord(c) < 128 for c in text):
        return text
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Translate this farmer's complaint to English. Return only the translation, nothing else:\n{text}"}],
        max_tokens=100,
        temperature=0
    )
    return response.choices[0].message.content.strip()

def diagnose(symptom_text: str, crop: str = None) -> dict:
    build_db()
    symptom_en = to_english(symptom_text)
    matches = query_disease(symptom_en, crop=crop, n=3)

    if not matches:
        return {"status": "unknown", "response": "I could not find any matching disease. Please contact KVK helpline 1551."}

    best = matches[0]

    if best["distance"] > UNKNOWN_THRESHOLD:
        return {
            "status": "unknown",
            "disease": None,
            "distance": best["distance"],
            "response": "I don't recognize this disease clearly. Please contact your local KVK or call Karnataka agriculture helpline 1551."
        }

    context = "\n\n".join([f"Disease: {m['disease']} ({m['crop']})\n{m['doc']}" for m in matches])

    prompt = f"""You are an expert agricultural advisor for Karnataka, India.
A farmer described: "{symptom_en}"
Crop: {crop or 'unknown'}

Closest matching diseases:
{context}

Give:
1. Disease name
2. Confidence: High / Medium / Low
3. Treatment (specific, actionable)
If not confident, recommend KVK helpline 1551.
Under 100 words. Direct. Like advising a farmer on a phone call."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.2
    )

    return {
        "status": "ok",
        "disease": best["disease"],
        "crop": best["crop"],
        "distance": best["distance"],
        "response": response.choices[0].message.content.strip()
    }

if __name__ == "__main__":
    tests = [
        ("holes in stem dead heart leaves drying center", "jowar"),
        ("leaves curling upward thick yellow no fruit", "tomato"),
        ("purple spots on wheat leaves rust color", "wheat"),
    ]
    for symptom, crop in tests:
        print(f"\n[QUERY] {crop}: {symptom}")
        result = diagnose(symptom, crop=crop)
        print(f"Status: {result['status']} | Disease: {result.get('disease')} | dist={result.get('distance')}")
        print(f"Response: {result['response']}")
