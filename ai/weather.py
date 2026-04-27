import os
import requests
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ESCALATION_NUMBER = "1800-180-1551"

# ── Weathercode → simple English description ──────────────────
WEATHERCODE_MAP = {
    0:  "Clear sky",
    1:  "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Foggy",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}


# ── Fetch forecast from Open-Meteo ────────────────────────────
def fetch_forecast(lat: float, lon: float) -> dict | None:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":     lat,
        "longitude":    lon,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weathercode",
            "windspeed_10m_max",
            "soil_moisture_0_to_1cm_mean",
        ]),
        "timezone":     "Asia/Kolkata",
        "forecast_days": 3,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Open-Meteo fetch failed: {e}")
        return None


# ── LLM: Answer farmer's specific question in Kannada ─────────
def answer_in_kannada(forecast_text: str, transcript: str, location: str) -> str:
    prompt = f"""You are a helpful agricultural assistant answering a Karnataka farmer's weather question in simple spoken Kannada.

Location: {location}

3-day weather forecast:
{forecast_text}

Farmer's question (may be in Kannada or English): "{transcript}"

Instructions:
- Answer ONLY what the farmer asked. Do not give extra information.
- If they asked about rain — tell them rain forecast clearly.
- If they asked about temperature — tell them max/min temp.
- If they asked about sowing/spraying — use rain and soil moisture to advise yes or no.
- Keep answer under 80 words.
- Speak in simple Kannada a rural farmer understands.
- End with the date so farmer knows which day you mean."""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"weather LLM failed: {e}")
        return (
            f"{location} havamana: Naalige male sambhava ide. "
            "Hechu vivaragalige 1800-180-1551 ge call maadi."
        )


# ── Main function — called by pipeline.py ─────────────────────
def get_forecast(
    coords: tuple,
    transcript: str = "",
    location: str = "your area",
    location_fallback: bool = False,
) -> dict:
    """
    Input:
        coords           : (lat, lon) — from intent_router DISTRICT_COORDS
        transcript       : farmer's original spoken question
        location         : district name for display
        location_fallback: True if we're using GPS/default instead of farmer-stated district

    Output:
        Unified JSON matching pipeline schema
    """
    lat, lon = coords

    raw = fetch_forecast(lat, lon)

    if not raw:
        return {
            "intent":           "weather",
            "status":           "error",
            "confidence":       "LOW",
            "response_text":    "Weather data unavailable. Please call 1800-180-1551.",
            "response_kannada": (
                "Kshamisi sir, ippol havamana mahiti siguttilla. "
                "Dayavittu 1800-180-1551 ge call maadi."
            ),
            "escalate":        True,
            "escalation_to":   ESCALATION_NUMBER,
            "card_data":       {"forecast": []}
        }

    daily = raw["daily"]
    days  = daily["time"]

    # ── Build forecast summary for LLM ───────────────────────
    forecast_lines = []
    card_forecast  = []

    for i in range(len(days)):
        code     = daily["weathercode"][i]
        desc     = WEATHERCODE_MAP.get(code, "Unknown")
        max_t    = daily["temperature_2m_max"][i]
        min_t    = daily["temperature_2m_min"][i]
        rain     = daily["precipitation_sum"][i]
        wind     = daily.get("windspeed_10m_max",        [None,None,None])[i]
        soil     = daily.get("soil_moisture_0_to_1cm_mean", [None,None,None])[i]

        label = "Today" if i == 0 else ("Tomorrow" if i == 1 else days[i])

        line = (
            f"{label} ({days[i]}): {desc}, "
            f"Max {max_t}°C / Min {min_t}°C, "
            f"Rain {rain}mm"
        )
        if wind is not None:
            line += f", Wind {wind}km/h"
        if soil is not None:
            line += f", Soil moisture {round(soil*100)}%"

        forecast_lines.append(line)
        card_forecast.append({
            "date":      days[i],
            "label":     label,
            "condition": desc,
            "max_temp":  max_t,
            "min_temp":  min_t,
            "rain_mm":   rain,
            "wind_kmh":  wind,
            "soil_moisture_pct": round(soil * 100) if soil is not None else None,
        })

    forecast_text = "\n".join(forecast_lines)

    # ── LLM answers farmer's specific question ────────────────
    kannada_response = answer_in_kannada(forecast_text, transcript, location)

    # ── English summary for logs/debugging ───────────────────
    response_text = f"Weather for {location}: " + " | ".join(forecast_lines)

    # Confidence — lower if using fallback location
    confidence = "MEDIUM" if location_fallback else "HIGH"

    return {
        "intent":           "weather",
        "status":           "ok",
        "confidence":       confidence,
        "response_text":    response_text,
        "response_kannada": kannada_response,
        "escalate":         False,
        "escalation_to":    None,
        "card_data": {
            "location":          location,
            "location_fallback": location_fallback,
            "forecast":          card_forecast,
        }
    }


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("WEATHER — TEST RUN")
    print("="*60)

    tests = [
        ((14.7957, 75.3997), "Haveri alli naale male barthaa?",        "Haveri",   False),
        ((12.9716, 77.5946), "Naale beeja biththa maadabahudhaa?",     "Bengaluru", True),
        ((15.3647, 75.1240), "Illi temperature eshtu ide naale?",      "Dharwad",  False),
    ]

    for coords, transcript, location, fallback in tests:
        print(f"\nLocation: {location} | Fallback: {fallback}")
        print(f"Question: {transcript}")
        result = get_forecast(coords, transcript, location, fallback)
        print(f"Status: {result['status']} | Confidence: {result['confidence']}")
        print(f"Kannada: {result['response_kannada'][:100]}...")
        print(f"Forecast days: {len(result['card_data']['forecast'])}")
