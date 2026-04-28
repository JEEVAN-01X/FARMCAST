import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ESCALATION_NUMBER = "1800-180-1551"

# ── Scheme Database ───────────────────────────────────────────
# priority: lower number = shown first to farmer
# 1 = cash benefit, 2 = crop-specific, 3 = credit, 4 = infrastructure, 5 = other
SCHEMES = [
    {
        "name": "PM-KISAN",
        "benefit": "Rs.6000/year in 3 instalments directly to bank account",
        "priority": 1,
        "eligibility": lambda crop, acres, state: acres > 0,
        "documents": ["Aadhaar card", "Land records (RTC)", "Bank account details"],
        "link": "https://pmkisan.gov.in",
        "note": None,
    },
    {
        "name": "Raitha Siri (Karnataka)",
        "benefit": "Input subsidy + quality seed kits for small farmers",
        "priority": 1,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and acres <= 2.5
        ),
        "documents": ["Aadhaar card", "RTC / land record", "FRUITS farmer ID", "Bank account"],
        "link": "https://raitamitra.karnataka.gov.in",
        "note": None,
    },
    {
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "benefit": "Crop insurance — covers loss due to drought, flood, pest",
        "priority": 2,
        "eligibility": lambda crop, acres, state: crop in [
            "jowar", "ragi", "paddy", "maize", "cotton",
            "groundnut", "sugarcane", "onion", "potato"
        ],
        "documents": ["Aadhaar card", "Land records (RTC)", "Bank account", "Sowing certificate"],
        "link": "https://pmfby.gov.in",
        "note": None,
    },
    {
        "name": "Bhoochetana (Karnataka)",
        "benefit": "Soil health + yield improvement program for dryland crops",
        "priority": 2,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and
            crop in ["jowar", "ragi", "maize", "cotton", "groundnut"]
        ),
        "documents": ["Aadhaar card", "RTC / land record", "FRUITS farmer ID"],
        "link": "https://raitamitra.karnataka.gov.in",
        "note": None,
    },
    {
        "name": "NFSM (National Food Security Mission)",
        "benefit": "Free seeds, inputs, training for food crop farmers",
        "priority": 2,
        "eligibility": lambda crop, acres, state: crop in [
            "paddy", "jowar", "ragi", "maize", "groundnut"
        ],
        "documents": ["Aadhaar card", "Land records (RTC)", "FRUITS farmer ID"],
        "link": "https://nfsm.gov.in",
        "note": None,
    },
    {
        "name": "KCC (Kisan Credit Card)",
        "benefit": "Crop loan up to Rs.3 lakh at 4% interest per year",
        "priority": 3,
        "eligibility": lambda crop, acres, state: acres > 0,
        "documents": ["Aadhaar card", "Land records (RTC)", "Passport photo", "Bank account"],
        "link": "https://www.nabard.org/content.aspx?id=572",
        "note": None,
    },
    {
        "name": "Soil Health Card Scheme",
        "benefit": "Free soil testing + fertiliser recommendation card",
        "priority": 3,
        "eligibility": lambda crop, acres, state: acres > 0,
        "documents": ["Aadhaar card", "Land records (RTC)"],
        "link": "https://soilhealth.dac.gov.in",
        "note": None,
    },
    {
        "name": "Krishi Bhagya (Karnataka)",
        "benefit": "Farm pond + pump set + poly cover — up to 80-90% subsidy for dryland farmers",
        "priority": 4,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and acres >= 1
        ),
        "documents": ["Aadhaar card", "RTC / land record", "FRUITS farmer ID"],
        "link": "https://raitamitra.karnataka.gov.in",
        "note": None,
    },
    {
        "name": "PM Krishi Sinchai Yojana",
        "benefit": "Subsidy on drip/sprinkler irrigation setup",
        "priority": 4,
        "eligibility": lambda crop, acres, state: acres >= 1,
        "documents": ["Aadhaar card", "Land records (RTC)", "Bank account", "Water source proof"],
        "link": "https://pmksy.gov.in",
        "note": None,
    },
    {
        "name": "Farm Mechanisation Scheme (Karnataka)",
        "benefit": "50% subsidy on tractors and farm equipment (90% for SC/ST farmers)",
        "priority": 4,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and acres >= 1
        ),
        "documents": ["Aadhaar card", "RTC / land record", "Caste certificate if SC/ST", "Bank account"],
        "link": "https://raitamitra.karnataka.gov.in",
        "note": None,
    },
    {
        "name": "eNAM (National Agriculture Market)",
        "benefit": "Online mandi access — sell crop at best price across India",
        "priority": 4,
        "eligibility": lambda crop, acres, state: acres > 0,
        "documents": ["Aadhaar card", "Bank account", "FRUITS farmer ID"],
        "link": "https://enam.gov.in",
        "note": None,
    },
    {
        "name": "RKVY (Rashtriya Krishi Vikas Yojana)",
        "benefit": "Project-based grants for crop diversification and farm infrastructure",
        "priority": 5,
        "eligibility": lambda crop, acres, state: acres > 0,
        "documents": ["Aadhaar card", "Land records (RTC)", "Project proposal"],
        "link": "https://rkvy.nic.in",
        "note": None,
    },
    {
        "name": "KAPY - Krushi Aranya Protsaha Yojane (Karnataka)",
        "benefit": "Subsidised seedlings + Rs.3000 incentive for planting trees on farm boundary",
        "priority": 5,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and acres >= 1
        ),
        "documents": ["Aadhaar card", "RTC / land record", "Pahani"],
        "link": "https://www.myscheme.gov.in/schemes/kapy",
        "note": None,
    },
    {
        "name": "Ganga Kalyana Scheme (Karnataka)",
        "benefit": "Free borewell + pump set + electrification for minority farmers",
        "priority": 5,
        "eligibility": lambda crop, acres, state: (
            state.lower() == "karnataka" and acres >= 1
        ),
        "documents": ["Aadhaar card", "RTC / land record", "Minority certificate", "Caste certificate", "Bank account"],
        "link": "https://sevasindhu.karnataka.gov.in",
        "note": "Only for farmers belonging to minority communities",
    },
    {
        "name": "PKVY (Paramparagat Krishi Vikas Yojana)",
        "benefit": "Rs.50,000/hectare for organic farming — requires group of 50 farmers",
        "priority": 5,
        "eligibility": lambda crop, acres, state: False,  # single farmer cannot qualify
        "documents": ["Aadhaar card", "Land records (RTC)", "Group of 50 farmers needed"],
        "link": "https://pgsindia-ncof.gov.in/PKVY/Index.aspx",
        "note": "Requires a group of 50 farmers — contact KVK to form a group",
    },
]


# ── LLM: Generate Kannada explanation ────────────────────────
def explain_in_kannada(eligible_schemes, crop, acres):
    if not eligible_schemes:
        return (
            "Kshamisi sir, nimma vivaragalige yava scheme siguvudilla. "
            "Dayavittu 1800-180-1551 ge call maadi."
        )

    # Top 5 by priority (already sorted before this call)
    top5 = eligible_schemes[:5]
    names_and_benefits = "\n".join(
        f"- {s['name']}: {s['benefit']} (Documents: {', '.join(s['documents'][:2])})" for s in top5
    )

    prompt = f"""You are a helpful assistant explaining Indian government schemes to a Karnataka farmer in simple spoken Kannada.

Farmer details:
- Crop: {crop if crop else 'not specified'}
- Land: {acres} acres
- State: Karnataka

Top eligible schemes:
{names_and_benefits}

Write a short, simple spoken Kannada explanation (under 120 words) telling the farmer:
1. How many schemes they qualify for
2. Name each scheme (keep English names as-is)
3. The single most important benefit of each
4. The top 2 documents they need to bring to apply
5. Tell them to visit nearest Raitha Samparka Kendra or call 1800-180-1551 to apply

Use simple Kannada a rural farmer would understand. No bullet points. Speak like talking on a phone call."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"explain_in_kannada LLM failed: {e}")
        names = ", ".join(s["name"] for s in top5)
        return (
            f"Sir, nimge {len(eligible_schemes)} scheme sigatte — {names}. "
            "Hechu vivaragalige 1800-180-1551 ge call maadi athava "
            "Raitha Samparka Kendra ge hogi."
        )


# ── Main function ─────────────────────────────────────────────
def get_schemes(
    crop: str | None,
    acres: float | None,
    state: str = "Karnataka",
    transcript: str = ""
) -> dict:

    crop  = (crop or "").lower().strip()
    acres = acres or 0.0
    state = state or "Karnataka"

    # Run eligibility check
    eligible = []
    for scheme in SCHEMES:
        try:
            if scheme["eligibility"](crop, acres, state):
                eligible.append(scheme)
        except Exception as e:
            logger.warning(f"Eligibility check failed for {scheme['name']}: {e}")

    # Sort by priority — cash benefits first, infrastructure last
    eligible.sort(key=lambda s: s["priority"])

    # Zero matches → escalate
    if not eligible:
        return {
            "intent":           "scheme",
            "status":           "escalate",
            "confidence":       "LOW",
            "response_text":    "No schemes found. Please call 1800-180-1551.",
            "response_kannada": (
                "Kshamisi sir, nimma vivaragalige yava scheme siguvudilla. "
                "Dayavittu 1800-180-1551 ge call maadi athava "
                "hattira Raitha Samparka Kendra ge hogi."
            ),
            "escalate":        True,
            "escalation_to":   "1800-180-1551",
            "card_data": {
                "eligible_schemes": []
            }
        }

    # Build card data — all eligible schemes for WhatsApp card
    card_schemes = []
    for s in eligible:
        entry = {
            "name":      s["name"],
            "benefit":   s["benefit"],
            "documents": s["documents"],
            "link":      s["link"],
        }
        if s.get("note"):
            entry["note"] = s["note"]
        card_schemes.append(entry)

    # Confidence based on data quality
    if crop and acres > 0:
        confidence = "HIGH"
    elif crop or acres > 0:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    kannada_response = explain_in_kannada(eligible, crop, acres)

    return {
        "intent":           "scheme",
        "status":           "ok",
        "confidence":       confidence,
        "response_text":    (
            f"Found {len(eligible)} eligible schemes: "
            f"{', '.join(s['name'] for s in eligible)}"
        ),
        "response_kannada": kannada_response,
        "escalate":         False,
        "escalation_to":    None,
        "card_data": {
            "eligible_schemes": card_schemes
        }
    }


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCHEME ENGINE — TEST RUN")
    print("="*60)

    tests = [
        ("jowar",  2.0,  "Karnataka"),   # small farmer, dryland crop
        ("paddy",  5.0,  "Karnataka"),   # medium farmer
        ("cotton", 1.5,  "Karnataka"),   # small farmer, cash crop
        ("areca",  3.0,  "Karnataka"),   # crop not in special lists
        (None,     0.0,  "Karnataka"),   # no info → escalate
    ]

    for crop, acres, state in tests:
        print(f"\nCrop: {crop} | Acres: {acres} | State: {state}")
        result = get_schemes(crop, acres, state)
        print(f"Status: {result['status']} | Confidence: {result['confidence']}")
        print(f"Schemes ({len(result['card_data']['eligible_schemes'])}):")
        for s in result['card_data']['eligible_schemes']:
            note = f" ⚠ {s['note']}" if s.get('note') else ""
            print(f"  → {s['name']}{note}")
        print(f"Kannada: {result['response_kannada'][:80]}...")
