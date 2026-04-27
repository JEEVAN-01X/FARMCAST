import os, subprocess
from groq import Groq
from gtts import gTTS
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DISEASES = [
    {"keywords": ["jowar", "sorghum", "stem", "hole", "borer", "caterpillar", "dead heart", "stalk"], "disease": "Jowar stem borer", "treatment": "spray chlorpyrifos"},
    {"keywords": ["jowar", "sorghum", "mildew", "fungal", "white", "streak", "stunted"], "disease": "Jowar downy mildew", "treatment": "spray metalaxyl"},
    {"keywords": ["ragi", "finger millet", "blast", "grey", "spot", "neck rot"], "disease": "Ragi blast", "treatment": "spray tricyclazole"},
    {"keywords": ["tomato", "blight", "water soaked", "mold", "patch"], "disease": "Tomato late blight", "treatment": "apply mancozeb"},
    {"keywords": ["cotton", "bollworm", "boll", "larvae", "square"], "disease": "Cotton bollworm", "treatment": "spray spinosad"},
    {"keywords": ["groundnut", "leaf spot", "brown spot", "yellow", "defoliation"], "disease": "Groundnut leaf spot", "treatment": "apply chlorothalonil"},
]

def transcribe(audio_file="test.wav"):
    with open(audio_file, "rb") as f:
        return client.audio.transcriptions.create(
            model="whisper-large-v3", file=f, language="kn", response_format="text"
        )

def detect_intent(query):
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": f"""Classify this farmer query into one word only:
- DISEASE (if about crop symptoms, pests, plant problems)
- PRICE (if about market price, mandi, rates)
- WEATHER (if about rain, temperature, forecast)
- UNKNOWN (anything else or unclear)

Query: '{query}'
Reply with one word only."""}],
        max_tokens=5
    )
    return resp.choices[0].message.content.strip().upper()

def match_disease(english_query):
    q = english_query.lower()
    best = None
    best_score = 0
    for d in DISEASES:
        score = sum(1 for kw in d["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best = d
    return best

def diagnose(query_kannada):
    query_english = GoogleTranslator(source='kn', target='en').translate(query_kannada)
    match = match_disease(query_english)
    if match and match != DISEASES[-1]:
        return f"Your crop has {match['disease']}. To treat it, {match['treatment']}."
    # Fallback to LLM if no keyword match
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": f"""Farmer says: '{query_english}'
From this list only, identify the disease and treatment:
{chr(10).join([f"- {d['disease']}: {d['treatment']}" for d in DISEASES])}
Reply in exactly 2 sentences. English only."""}],
        max_tokens=80
    )
    return resp.choices[0].message.content.strip()

def speak(english_text):
    kannada = GoogleTranslator(source='en', target='kn').translate(english_text)
    print(f"Kannada: {kannada}")
    gTTS(text=kannada, lang="kn").save("response.mp3")
    subprocess.run(["mpg123", "-q", "response.mp3"])

print("=== FARMCAST ===")
print("Transcribing...")
query = transcribe("test.wav")
print(f"Farmer said: {query}")

print("Detecting intent...")
intent = detect_intent(query)
print(f"Intent: {intent}")

if intent == "DISEASE":
    advice = diagnose(query)
    print(f"Advice: {advice}")
    speak(advice)
elif intent == "PRICE":
    speak("You asked about market price. Please check your local mandi or ask again for crop disease help.")
elif intent == "WEATHER":
    speak("You asked about weather. I can help with crop diseases. Please describe your crop symptoms.")
else:
    speak("I did not understand. Please describe your crop problem clearly.")

print("Done.")
