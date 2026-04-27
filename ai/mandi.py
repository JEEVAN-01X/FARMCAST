import os
import requests
from dotenv import load_dotenv

load_dotenv()

MANDI_API_KEY = os.getenv("MANDI_API_KEY", "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b")
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

CROP_ALIASES = {
    "jowar": "Jowar(Sorghum)",
    "ragi": "Ragi (Finger Millet)",
    "tomato": "Tomato",
    "cotton": "Cotton",
    "groundnut": "Groundnut",
    "maize": "Maize",
    "onion": "Onion",
    "potato": "Potato",
}

def get_mandi_price(commodity: str, state: str = "Karnataka", limit: int = 5) -> list:
    """
    Fetch current mandi prices for a commodity.
    Returns list of dicts with market, min_price, max_price, modal_price, date.
    """
    commodity_name = CROP_ALIASES.get(commodity.lower(), commodity)
    
    params = {
        "api-key": MANDI_API_KEY,
        "format": "json",
        "filters[state.keyword]": state,
        "filters[commodity]": commodity_name,
        "limit": limit,
        "offset": 0
    }
    
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        records = data.get("records", [])
        
        results = []
        for rec in records:
            results.append({
                "market":      rec.get("market", ""),
                "district":    rec.get("district", ""),
                "state":       rec.get("state", ""),
                "commodity":   rec.get("commodity", ""),
                "variety":     rec.get("variety", ""),
                "min_price":   rec.get("min_price", ""),
                "max_price":   rec.get("max_price", ""),
                "modal_price": rec.get("modal_price", ""),
                "arrival_date": rec.get("arrival_date", ""),
            })
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"[mandi] API error: {e}")
        return []

def format_price_summary(commodity: str, state: str = "Karnataka") -> str:
    """Human-readable price summary for farmer."""
    prices = get_mandi_price(commodity, state)
    if not prices:
        return f"Could not fetch current prices for {commodity}. Try again later."
    
    lines = [f"Today's {commodity.title()} prices in {state}:"]
    for p in prices:
        lines.append(
            f"  {p['market']} ({p['district']}): ₹{p['modal_price']}/quintal "
            f"[min ₹{p['min_price']} – max ₹{p['max_price']}] on {p['arrival_date']}"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    for crop in ["tomato", "jowar", "ragi", "onion"]:
        print(f"\n{'='*50}")
        print(format_price_summary(crop))
