import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── IVR Scripts ────────────────────────────────────────────────
IVR_WELCOME = (
    "FarmCast ge swagata. "
    "Roga problem ge one. "
    "Bele price ge two. "
    "Yojane bekandre three. "
    "Havamana bekandre four. "
    "Bere vishaya bekandre five."
)

IVR_PROMPT = "Namaskara, nimige naminda en sahaya agabeku? Heli sir."

IVR_INVALID = (
    "Kshamisi, aa number sigalilla. "
    "Roga problem ge one. "
    "Bele price ge two. "
    "Yojane bekandre three. "
    "Havamana bekandre four. "
    "Bere vishaya bekandre five."
)

IVR_REPEAT = "Kshamisi, nimma maathu gottaagalilla. Dayavittu matte heli sir."

# ── DTMF → Intent map ─────────────────────────────────────────
DTMF_MAP = {
    "1": "disease",
    "2": "price",
    "3": "scheme",
    "4": "weather",
    "5": "general",
}

# ── Crop keywords ─────────────────────────────────────────────
CROP_MAP = {
    "jowar":      ["jowar", "jola", "ಜೋಳ", "jolaa"],
    "ragi":       ["ragi", "raagi", "ರಾಗಿ", "finger millet"],
    "tomato":     ["tomato", "ಟೊಮೇಟೊ", "tamatar", "tomato"],
    "cotton":     ["cotton", "hatti", "ಹತ್ತಿ", "kapas"],
    "groundnut":  ["groundnut", "kadalekayi", "ಕಡಲೆಕಾಯಿ", "peanut", "kadala"],
    "maize":      ["maize", "corn", "makka", "ಮೆಕ್ಕೆಜೋಳ", "mekke jola"],
    "onion":      ["onion", "eerulli", "ಈರುಳ್ಳಿ", "pyaz"],
    "potato":     ["potato", "aloo", "ಆಲೂಗಡ್ಡೆ", "aaloo gadde"],
    "sugarcane":  ["sugarcane", "kabbu", "ಕಬ್ಬು", "ganna"],
    "areca":      ["areca", "arecanut", "adike", "ಅಡಿಕೆ", "supari"],
    "coconut":    ["coconut", "tenginakaayi", "ಮತ", "naryal"],
    "paddy":      ["paddy", "rice", "akki", "ಅಕ್ಕಿ", "dhan", "bhatta"],
}

# ── District keywords ─────────────────────────────────────────
DISTRICT_MAP = {
    "haveri":     ["haveri", "ಹಾವೇರಿ"],
    "dharwad":    ["dharwad", "dharwar", "ಧಾರವಾಡ"],
    "belgaum":    ["belgaum", "belagavi", "ಬೆಳಗಾವಿ"],
    "bijapur":    ["bijapur", "vijayapura", "ಬಿಜಾಪುರ"],
    "gulbarga":   ["gulbarga", "kalaburagi", "ಕಲಬುರಗಿ"],
    "raichur":    ["raichur", "ರಾಯಚೂರು"],
    "mysore":     ["mysore", "mysuru", "ಮೈಸೂರು"],
    "tumkur":     ["tumkur", "tumakuru", "ತುಮಕೂರು"],
    "Hassan":     ["hassan", "ಹಾಸನ"],
    "bangalore":  ["bangalore", "bengaluru", "ಬೆಂಗಳೂರು"],
    "mandya":     ["mandya", "ಮಂಡ್ಯ"],
    "shimoga":    ["shimoga", "shivamogga", "ಶಿವಮೊಗ್ಗ"],
    "chitradurga":["chitradurga", "ಚಿತ್ರದುರ್ಗ"],
    "davanagere": ["davanagere", "davangere", "ದಾವಣಗೆರೆ"],
    "bellary":    ["bellary", "ballari", "ಬಳ್ಳಾರಿ"],
    "bidar":      ["bidar", "ಬೀದರ್"],
    "koppal":     ["koppal", "ಕೊಪ್ಪಳ"],
    "gadag":      ["gadag", "ಗದಗ"],
    "bagalkot":   ["bagalkot", "ಬಾಗಲಕೋಟೆ"],
    "udupi":      ["udupi", "ಉಡುಪಿ"],
    "dakshina":   ["dakshina kannada", "mangalore", "mangaluru", "ಮಂಗಳೂರು"],
}

# ── Default district lat/lon (fallback = Bengaluru) ───────────
DISTRICT_COORDS = {
    "haveri":      (14.7957, 75.3997),
    "dharwad":     (15.4589, 75.0078),
    "belgaum":     (15.8497, 74.4977),
    "bijapur":     (16.8302, 75.7100),
    "gulbarga":    (17.3297, 76.8343),
    "raichur":     (16.2120, 77.3439),
    "mysore":      (12.2958, 76.6394),
    "tumkur":      (13.3379, 77.1173),
    "hassan":      (13.0068, 76.1004),
    "bangalore":   (12.9716, 77.5946),
    "mandya":      (12.5218, 76.8951),
    "shimoga":     (13.9299, 75.5681),
    "chitradurga": (14.2251, 76.3980),
    "davanagere":  (14.4644, 75.9218),
    "bellary":     (15.1394, 76.9214),
    "bidar":       (17.9104, 77.5199),
    "koppal":      (15.3514, 76.1544),
    "gadag":       (15.4166, 75.6278),
    "bagalkot":    (16.1826, 75.6961),
    "udupi":       (13.3409, 74.7421),
    "dakshina":    (12.9141, 74.8560),
}
DEFAULT_COORDS = (12.9716, 77.5946)  # Bengaluru fallback


def extract_crop(text: str) -> str | None:
    """Extract crop name from transcript using keyword matching."""
    text_lower = text.lower()
    for crop, keywords in CROP_MAP.items():
        if any(k in text_lower for k in keywords):
            return crop
    return None


def extract_district(text: str) -> str | None:
    """Extract district name from transcript."""
    text_lower = text.lower()
    for district, keywords in DISTRICT_MAP.items():
        if any(k in text_lower for k in keywords):
            return district
    return None


def get_coords(district: str | None) -> tuple[float, float]:
    """Return lat/lon for district, fallback to Bengaluru."""
    if district and district.lower() in DISTRICT_COORDS:
        return DISTRICT_COORDS[district.lower()]
    return DEFAULT_COORDS


def llm_extract(transcript: str) -> dict:
    """
    Use LLM to extract crop, district, and symptoms from transcript.
    Called only when keyword matching fails.
    """
    prompt = f"""Extract information from this farmer's message. Return JSON only, no explanation.

Message: "{transcript}"

Return exactly this JSON:
{{
  "crop": "crop name in english or null",
  "district": "district name in karnataka or null",
  "symptoms": "brief symptom description in english or null"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )
        import json
        raw = response.choices[0].message.content.strip()
        # Strip markdown if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return {"crop": None, "district": None, "symptoms": None}


def route(dtmf: str, transcript: str = "") -> dict:
    """
    Main routing function.

    Input:
        dtmf       : "1" | "2" | "3" | "4" | "5"
        transcript : farmer's spoken text (Kannada or English)

    Output:
        {
            "intent"    : "disease" | "price" | "scheme" | "weather" | "general",
            "crop"      : str | None,
            "district"  : str | None,
            "coords"    : (lat, lon),
            "symptoms"  : str | None,
            "transcript": str,
            "ivr_prompt": str,   # what to play before listening
            "valid"     : bool
        }
    """
    # Validate DTMF
    if dtmf not in DTMF_MAP:
        return {
            "intent":     None,
            "valid":      False,
            "ivr_prompt": IVR_INVALID,
            "crop":       None,
            "district":   None,
            "coords":     DEFAULT_COORDS,
            "symptoms":   None,
            "transcript": transcript,
        }

    intent = DTMF_MAP[dtmf]

    # Fast keyword extraction first
    crop     = extract_crop(transcript)
    district = extract_district(transcript)
    symptoms = None

    # If transcript exists but keywords didn't catch crop/district → use LLM
    if transcript.strip() and (crop is None or district is None):
        llm_data = llm_extract(transcript)
        crop     = crop     or llm_data.get("crop")
        district = district or llm_data.get("district")
        symptoms = llm_data.get("symptoms")

    coords = get_coords(district)

    return {
        "intent":     intent,
        "valid":      True,
        "ivr_prompt": IVR_PROMPT,
        "crop":       crop,
        "district":   district,
        "coords":     coords,
        "symptoms":   symptoms,
        "transcript": transcript,
    }


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("1", "nanna jola bele mele bili chukke banthive haveri district alli"),
        ("2", "tomato bele eshtu ide tumkur alli"),
        ("3", "PM kisan yojane nakku siguta ide"),
        ("4", "naale male barthaa"),
        ("5", "nanna hola alli neeru niltailla"),
        ("9", ""),  # invalid DTMF
    ]

    print("\n" + "="*60)
    print("INTENT ROUTER — TEST RUN")
    print("="*60)

    for dtmf, text in tests:
        result = route(dtmf, text)
        print(f"\nDTMF  : {dtmf}")
        print(f"INPUT : {text}")
        print(f"INTENT: {result['intent']} | VALID: {result['valid']}")
        print(f"CROP  : {result['crop']} | DISTRICT: {result['district']}")
        print(f"COORDS: {result['coords']}")
        print(f"SYMPTOMS: {result['symptoms']}")
        print(f"IVR   : {result['ivr_prompt']}")
