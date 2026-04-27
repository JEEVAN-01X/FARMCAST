import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MANDI_API_KEY = os.getenv("MANDI_API_KEY", "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

CACHE_TTL = 86400  # 24 hours

CROP_ALIASES = {
    "jowar":      "Jowar(Sorghum)",
    "ragi":       "Ragi (Finger Millet)",
    "tomato":     "Tomato",
    "cotton":     "Cotton",
    "groundnut":  "Groundnut",
    "maize":      "Maize",
    "onion":      "Onion",
    "potato":     "Potato",
}


# ── Redis connection (optional — degrades gracefully if Redis down) ──
def _get_redis():
    try:
        import redis
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            socket_connect_timeout=1,
            decode_responses=True,
        )
        r.ping()
        return r
    except Exception:
        logger.warning("Redis unavailable — mandi running without cache")
        return None


# ── Cache helpers ─────────────────────────────────────────────
def _cache_key(commodity: str, state: str) -> str:
    return f"mandi:{state.lower()}:{commodity.lower()}"


def _from_cache(r, key: str):
    try:
        val = r.get(key)
        if val:
            return json.loads(val)
    except Exception:
        pass
    return None


def _to_cache(r, key: str, data: list):
    try:
        r.setex(key, CACHE_TTL, json.dumps(data))
    except Exception:
        pass


# ── Main fetch ────────────────────────────────────────────────
def get_mandi_price(commodity: str, state: str = "Karnataka", limit: int = 5) -> list:
    """
    Fetch mandi prices. Redis cache first (24hr TTL).
    Falls back to last cached value if API is down.
    Returns list of dicts. Each dict has a 'stale' key (True if from old cache).
    """
    commodity_name = CROP_ALIASES.get(commodity.lower(), commodity)
    r = _get_redis()
    key = _cache_key(commodity, state)

    # ── Cache hit ─────────────────────────────────────────────
    if r:
        cached = _from_cache(r, key)
        if cached:
            logger.info(f"[mandi] cache hit: {key}")
            return cached

    # ── Live API call ─────────────────────────────────────────
    params = {
        "api-key":                   MANDI_API_KEY,
        "format":                    "json",
        "filters[state.keyword]":    state,
        "filters[commodity]":        commodity_name,
        "limit":                     limit,
        "offset":                    0,
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        records = resp.json().get("records", [])

        results = []
        for rec in records:
            results.append({
                "market":       rec.get("market", ""),
                "district":     rec.get("district", ""),
                "state":        rec.get("state", ""),
                "commodity":    rec.get("commodity", ""),
                "variety":      rec.get("variety", ""),
                "min_price":    rec.get("min_price", ""),
                "max_price":    rec.get("max_price", ""),
                "modal_price":  rec.get("modal_price", ""),
                "arrival_date": rec.get("arrival_date", ""),
                "stale":        False,
            })

        if results and r:
            _to_cache(r, key, results)
            logger.info(f"[mandi] cached {len(results)} records for {key}")

        return results

    except requests.exceptions.RequestException as e:
        logger.error(f"[mandi] API error: {e}")

        # ── API down — try stale cache ────────────────────────
        if r:
            stale_key = f"{key}:stale"
            stale = _from_cache(r, stale_key)
            if stale:
                logger.warning(f"[mandi] serving stale cache for {key}")
                for item in stale:
                    item["stale"] = True
                return stale

        return []


# ── Human-readable summary ────────────────────────────────────
def format_price_summary(commodity: str, state: str = "Karnataka") -> str:
    prices = get_mandi_price(commodity, state)

    if not prices:
        return (
            f"Could not fetch current prices for {commodity}. "
            "Please check mandi.indiaagristat.com or call 1800-180-1551."
        )

    stale_note = " (last known prices — live data unavailable)" if prices[0].get("stale") else ""
    lines = [f"Today's {commodity.title()} prices in {state}{stale_note}:"]

    for p in prices:
        lines.append(
            f"  {p['market']} ({p['district']}): "
            f"₹{p['modal_price']}/quintal "
            f"[min ₹{p['min_price']} – max ₹{p['max_price']}] "
            f"on {p['arrival_date']}"
        )

    return "\n".join(lines)


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("MANDI — TEST RUN")
    print("="*60)
    for crop in ["tomato", "jowar", "ragi", "onion"]:
        print(f"\n{'-'*50}")
        print(format_price_summary(crop))
