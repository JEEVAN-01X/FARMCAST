import os
import logging
from groq import Groq
from dotenv import load_dotenv
from disease_db import query_disease, build_db

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UNKNOWN_THRESHOLD = 1.2

# ── Build ChromaDB once at startup, not on every call ────────
build_db()
logger.info("disease_db loaded at startup")


# ── Translate non-English input to English ───────────────────
def to_english(text: str) -> str:
    if all(ord(c) < 128 for c in text):
        return text
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": (
                "Translate this farmer's complaint to English. "
                "Return only the translation, nothing else:\n" + text
            )
        }],
        max_tokens=100,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


# ── Parse confidence level from LLaMA response text ──────────
def _parse_confidence(text: str) -> str:
    """
    Extracts High / Medium / Low from LLaMA response.
    Falls back to 'Low' if not found.
    """
    lower = text.lower()
    if "confidence: high" in lower or "high confidence" in lower:
        return "High"
    if "confidence: medium" in lower or "medium confidence" in lower:
        return "Medium"
    return "Low"


# ── Main diagnosis function ───────────────────────────────────
def diagnose(symptom_text: str, crop: str = None) -> dict:
    """
    Input : symptom text (any language), optional crop name
    Output: dict with keys —
        status         : "ok" | "unknown"
        disease        : str | None
        crop           : str | None
        distance       : float | None
        confidence_level: "High" | "Medium" | "Low"
        response       : str  (farmer-facing advice)
    """
    symptom_en = to_english(symptom_text)
    matches = query_disease(symptom_en, crop=crop, n=3)

    if not matches:
        return {
            "status": "unknown",
            "disease": None,
            "crop": None,
            "distance": None,
            "confidence_level": "Low",
            "response": (
                "I could not find any matching disease. "
                "Please contact KVK helpline 1551."
            ),
        }

    best = matches[0]

    if best["distance"] > UNKNOWN_THRESHOLD:
        return {
            "status": "unknown",
            "disease": None,
            "crop": None,
            "distance": best["distance"],
            "confidence_level": "Low",
            "response": (
                "I don't recognize this disease clearly. "
                "Please contact your local KVK or call Karnataka "
                "agriculture helpline 1551."
            ),
        }

    context = "\n\n".join([
        f"Disease: {m['disease']} ({m['crop']})\n{m['doc']}"
        for m in matches
    ])

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

    llm_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.2,
    )

    response_text = llm_response.choices[0].message.content.strip()

    return {
        "status": "ok",
        "disease": best["disease"],
        "crop": best["crop"],
        "distance": best["distance"],
        "confidence_level": _parse_confidence(response_text),
        "response": response_text,
    }


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("holes in stem dead heart leaves drying center", "jowar"),
        ("leaves curling upward thick yellow no fruit", "tomato"),
        ("purple spots on wheat leaves rust color", "wheat"),
    ]
    print("\n" + "="*60)
    print("DIAGNOSE — TEST RUN")
    print("="*60)
    for symptom, crop in tests:
        print(f"\n[QUERY] {crop}: {symptom}")
        result = diagnose(symptom, crop=crop)
        print(f"Status  : {result['status']}")
        print(f"Disease : {result.get('disease')}")
        print(f"Distance: {result.get('distance')}")
        print(f"Confidence: {result.get('confidence_level')}")
        print(f"Response: {result['response']}")
