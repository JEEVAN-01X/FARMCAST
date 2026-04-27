import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MARKET_TRENDS = {
    "tomato":     {"trend": "rising",  "avg_price_12m": 2800, "peak_months": "March–June",        "demand": "high",      "reason": "Processing industry demand up 18%. Export to Middle East increasing."},
    "onion":      {"trend": "stable",  "avg_price_12m": 1600, "peak_months": "November–January",   "demand": "high",      "reason": "Consistent domestic demand. Government buffer stock procurement active."},
    "jowar":      {"trend": "stable",  "avg_price_12m": 2400, "peak_months": "October–December",   "demand": "medium",    "reason": "MSP support keeps floor price stable. Ethanol blending may increase demand."},
    "ragi":       {"trend": "rising",  "avg_price_12m": 3000, "peak_months": "November–February",  "demand": "high",      "reason": "Urban health food demand surging. Millets mission pushing procurement prices up."},
    "maize":      {"trend": "rising",  "avg_price_12m": 2100, "peak_months": "September–November", "demand": "very high", "reason": "Poultry feed demand at record high. Ethanol policy creating additional buyers."},
    "groundnut":  {"trend": "stable",  "avg_price_12m": 5500, "peak_months": "December–February",  "demand": "medium",    "reason": "Edible oil import substitution policy supports domestic prices."},
    "cotton":     {"trend": "falling", "avg_price_12m": 6200, "peak_months": "October–November",   "demand": "low",       "reason": "Global cotton glut. Textile export orders down. Consider switching next season."},
    "potato":     {"trend": "stable",  "avg_price_12m": 1200, "peak_months": "January–March",      "demand": "medium",    "reason": "Cold storage in Karnataka limited — price volatility risk."},
}

DISTRICT_CROP_FIT = {
    "haveri":      ["jowar", "cotton", "maize", "groundnut"],
    "davangere":   ["ragi", "jowar", "maize", "groundnut"],
    "raichur":     ["jowar", "cotton", "maize"],
    "koppal":      ["jowar", "groundnut", "cotton"],
    "dharwad":     ["jowar", "maize", "groundnut", "cotton"],
    "gadag":       ["jowar", "maize", "groundnut"],
    "belgaum":     ["jowar", "maize", "groundnut", "cotton"],
    "bangalore":   ["tomato", "ragi", "potato", "onion"],
    "kolar":       ["tomato", "potato", "ragi"],
    "tumkur":      ["groundnut", "tomato", "ragi"],
    "mysore":      ["ragi", "maize", "tomato"],
    "hassan":      ["ragi", "potato", "maize"],
    "shimoga":     ["maize", "ragi"],
    "chitradurga": ["groundnut", "jowar", "ragi"],
    "bellary":     ["jowar", "cotton", "groundnut"],
}


def get_recommendation(current_crop: str, district: str) -> dict:
    district_lower = district.lower().strip()
    current_lower  = current_crop.lower().strip()

    suitable = DISTRICT_CROP_FIT.get(district_lower, list(MARKET_TRENDS.keys()))

    scored = []
    for crop in suitable:
        if crop == current_lower:
            continue
        t = MARKET_TRENDS.get(crop)
        if not t:
            continue
        score = 0
        if t["trend"] == "rising":     score += 3
        elif t["trend"] == "stable":   score += 1
        elif t["trend"] == "falling":  score -= 2
        if t["demand"] == "very high": score += 3
        elif t["demand"] == "high":    score += 2
        elif t["demand"] == "medium":  score += 1
        scored.append((score, crop))

    if not scored:
        return {
            "status":           "no_data",
            "current_crop":     current_crop,
            "district":         district,
            "recommendation":   None,
            "response_text":    f"No market data for {district}. Contact your KVK officer.",
            "response_kannada": f"Nimma {district} district ge market data illa. KVK officerge call maadi.",
        }

    scored.sort(reverse=True)
    best_crop = scored[0][1]
    best_data = MARKET_TRENDS[best_crop]
    current_data = MARKET_TRENDS.get(current_lower, {})

    prompt = f"""You are an agricultural market advisor for Karnataka farmers.
Current crop: {current_crop} | District: {district}
Recommended crop for next season: {best_crop}
- Price trend: {best_data['trend']}
- Average price last 12 months: ₹{best_data['avg_price_12m']}/quintal
- Peak selling months: {best_data['peak_months']}
- Demand: {best_data['demand']}
- Reason: {best_data['reason']}
Current crop ({current_crop}) trend: {current_data.get('trend', 'unknown')}

Give the farmer 3 sentences: what to plant, best months to sell, how it compares to current crop.
Under 80 words. Simple English. Like talking to a farmer on a phone call.
Then on a new line: KANNADA: [translate to simple spoken Kannada]"""

    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        full = r.choices[0].message.content.strip()
        if "KANNADA:" in full:
            parts = full.split("KANNADA:", 1)
            response_text    = parts[0].strip()
            response_kannada = parts[1].strip()
        else:
            response_text    = full
            response_kannada = full
    except Exception as e:
        logger.error(f"market_advisor LLM failed: {e}")
        response_text    = f"Plant {best_crop} next season. Trend is {best_data['trend']}, demand is {best_data['demand']}. Best selling months: {best_data['peak_months']}."
        response_kannada = response_text

    return {
        "status":           "ok",
        "current_crop":     current_crop,
        "district":         district,
        "recommendation":   best_crop,
        "trend":            best_data["trend"],
        "avg_price":        best_data["avg_price_12m"],
        "peak_months":      best_data["peak_months"],
        "demand":           best_data["demand"],
        "response_text":    response_text,
        "response_kannada": response_kannada,
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MARKET ADVISOR — TEST RUN")
    print("="*60)
    for crop, district in [("cotton", "haveri"), ("jowar", "davangere"), ("groundnut", "tumkur")]:
        print(f"\n[QUERY] Current: {crop} | District: {district}")
        r = get_recommendation(crop, district)
        print(f"Recommendation : {r.get('recommendation')} | Trend: {r.get('trend')} | Demand: {r.get('demand')}")
        print(f"Response (EN)  : {r['response_text']}")
        print(f"Response (KN)  : {r['response_kannada']}")
