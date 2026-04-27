import os
import logging
from dotenv import load_dotenv
from groq import Groq

import intent_router
import diagnose
import mandi
import scheme_engine
import weather

load_dotenv()
logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────
ESCALATION_NUMBER = "1800-180-1551"

ESCALATION_KANNADA = (
    "Kshamisi sir, nimma maathu sari gottaagalilla. "
    "Dayavittu nimma huchchara athava KVK officerge call maadi. "
    "Farmer helpline number: 1800-180-1551. Dhanyavaada."
)

REQUIRED_FIELDS = {
    "disease": ["crop"],
    "price":   ["crop", "district"],
    "scheme":  ["crop", "acres"],
    "weather": ["district"],
    "general": [],
}

RETRY_PROMPTS = {
    "crop":     "Nimma bele hesaru heli sir.",
    "district": "Nimma district hesaru heli sir.",
    "acres":    "Nimma hola eshtu acre ide antha heli sir.",
}


# ── Validate ──────────────────────────────────────────────────
def validate(intent, router_output):
    required = REQUIRED_FIELDS.get(intent, [])
    missing = []
    for field in required:
        if not router_output.get(field):
            missing.append(field)
    return missing


# ── Merge round 1 + round 2 ───────────────────────────────────
def merge(round1, round2):
    merged = round1.copy()
    for key in ["crop", "district", "acres", "symptoms"]:
        if not merged.get(key) and round2.get(key):
            merged[key] = round2[key]
    return merged


# ── General intent handler ────────────────────────────────────
def handle_general(transcript):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful agricultural advisor for Karnataka farmers. "
                        "Answer in simple English under 100 words. "
                        "Then translate your answer to simple spoken Kannada."
                    )
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],
            max_tokens=200,
            temperature=0.4,
        )
        text = response.choices[0].message.content.strip()
        return {
            "intent":           "general",
            "status":           "ok",
            "confidence":       "MEDIUM",
            "response_text":    text,
            "response_kannada": text,
            "escalate":         False,
            "escalation_to":    None,
            "card_data":        {}
        }
    except Exception as e:
        logger.error(f"handle_general failed: {e}")
        return error_response("general")


# ── Route to correct module ───────────────────────────────────
def route_to_module(intent, data):
    crop       = data.get("crop")
    district   = data.get("district")
    acres      = data.get("acres") or 1.0
    coords     = data.get("coords")
    symptoms   = data.get("symptoms")
    transcript = data.get("transcript", "")

    try:
        if intent == "disease":
            return diagnose.diagnose(crop, symptoms, district)

        elif intent == "price":
            return mandi.get_price(crop, district)

        elif intent == "scheme":
            return scheme_engine.get_schemes(crop, acres, "Karnataka", transcript)

        elif intent == "weather":
            forecast = weather.get_forecast(coords)
            # If farmer mentioned a crop — append market recommendation
            if crop:
                try:
                    import market_advisor
                    market = market_advisor.get_recommendation(crop, district or "Karnataka")
                    if market.get("status") == "ok":
                        forecast["market_advice"] = {
                            "recommendation": market["recommendation"],
                            "trend":          market["trend"],
                            "peak_months":    market["peak_months"],
                            "avg_price":      market["avg_price"],
                        }
                        # Append to Kannada response so TTS reads it out
                        forecast["response_kannada"] = (
                            forecast.get("response_kannada", "") +
                            " " + market["response_kannada"]
                        ).strip()
                        forecast["response_text"] = (
                            forecast.get("response_text", "") +
                            " " + market["response_text"]
                        ).strip()
                except Exception as e:
                    logger.warning(f"market_advisor failed: {e}")
            return forecast

        elif intent == "general":
            return handle_general(transcript)

    except Exception as e:
        logger.error(f"route_to_module failed for {intent}: {e}")
        return error_response(intent)


# ── Standard error response ───────────────────────────────────
def error_response(intent):
    return {
        "intent":           intent,
        "status":           "error",
        "confidence":       "LOW",
        "response_text":    "Sorry, something went wrong. Please call 1800-180-1551.",
        "response_kannada": ESCALATION_KANNADA,
        "escalate":         True,
        "escalation_to":    ESCALATION_NUMBER,
        "needs_retry":      False,
        "retry_prompt":     None,
        "card_data":        {}
    }


# ── MAIN FUNCTION — called by api.py ─────────────────────────
def run(dtmf, transcript_1, transcript_2=None):
    """
    Input:
        dtmf         : "1" | "2" | "3" | "4" | "5"
        transcript_1 : farmer's first recording (always present)
        transcript_2 : farmer's second recording (only if retry happened)

    Output:
        Unified JSON — same shape every time regardless of intent.
        If needs_retry is True — api.py must play retry_prompt and record again.
        If escalate is True — api.py plays response_kannada and hangs up.
    """

    # ── Round 1 ───────────────────────────────────────────────
    r1 = intent_router.route(dtmf, transcript_1)

    # Invalid DTMF
    if not r1["valid"]:
        return {
            "intent":           None,
            "status":           "error",
            "confidence":       "LOW",
            "response_text":    "Invalid input.",
            "response_kannada": intent_router.IVR_INVALID,
            "escalate":         False,
            "escalation_to":    None,
            "needs_retry":      False,
            "retry_prompt":     None,
            "card_data":        {}
        }

    intent  = r1["intent"]
    missing = validate(intent, r1)

    # Round 1 has everything → route directly
    if not missing:
        result = route_to_module(intent, r1)
        result["needs_retry"]  = False
        result["retry_prompt"] = None
        return result

    # Round 1 missing something → ask farmer once more
    if transcript_2 is None:
        return {
            "intent":           intent,
            "status":           "ok",
            "confidence":       "LOW",
            "response_text":    "",
            "response_kannada": "",
            "escalate":         False,
            "escalation_to":    None,
            "needs_retry":      True,
            "retry_prompt":     RETRY_PROMPTS.get(missing[0]),
            "card_data":        {}
        }

    # ── Round 2 ───────────────────────────────────────────────
    r2     = intent_router.route(dtmf, transcript_2)
    merged = merge(r1, r2)
    missing_after_retry = validate(intent, merged)

    # Still missing after 2 tries
    if missing_after_retry:
        # Weather is special — never escalate, use default coords silently
        if intent == "weather":
            from intent_router import DEFAULT_COORDS
            merged["coords"]            = merged.get("coords") or DEFAULT_COORDS
            merged["location_fallback"] = True
            merged["district"]          = merged.get("district") or "your area"
            result = route_to_module(intent, merged)
            result["needs_retry"]  = False
            result["retry_prompt"] = None
            return result
        # All other intents → escalate + hang up
        return {
            "intent":           intent,
            "status":           "escalate",
            "confidence":       "LOW",
            "response_text":    "Sorry, we could not understand. Please call 1800-180-1551.",
            "response_kannada": ESCALATION_KANNADA,
            "escalate":         True,
            "escalation_to":    ESCALATION_NUMBER,
            "needs_retry":      False,
            "retry_prompt":     None,
            "card_data":        {}
        }

    # Got everything in Round 2 → route to module
    result = route_to_module(intent, merged)
    result["needs_retry"]  = False
    result["retry_prompt"] = None
    return result


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    import json

    print("\n" + "="*60)
    print("PIPELINE — TEST RUN")
    print("="*60)

    # Test 1: Disease — crop given in round 1
    print("\nTest 1: Disease with crop")
    r = run("1", "nanna jola bele mele bili chukke banthive haveri district alli")
    print(f"Status: {r['status']} | Confidence: {r['confidence']} | Retry: {r.get('needs_retry')}")

    # Test 2: Scheme — crop missing in round 1, given in round 2
    print("\nTest 2: Scheme — missing crop, retry")
    r = run("3", "nanu 2 acre ide yav scheme siguthe", None)
    print(f"Needs retry: {r.get('needs_retry')} | Retry prompt: {r.get('retry_prompt')}")

    r2 = run("3", "nanu 2 acre ide yav scheme siguthe", "nanu jowar belitini")
    print(f"Status: {r2['status']} | Confidence: {r2['confidence']}")

    # Test 3: 2 failed attempts → escalate
    print("\nTest 3: 2 failed attempts")
    r = run("2", "bele eshtu ide", "naale barthini")
    print(f"Status: {r['status']} | Escalate: {r['escalate']} | To: {r['escalation_to']}")
