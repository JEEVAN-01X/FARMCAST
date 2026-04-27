import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_mandi_price(crop="Jowar", state="Karnataka"):
    api_key = os.getenv("DATA_GOV_API_KEY")
    
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": api_key,
        "format": "json",
        "filters[state.keyword]": state,
        "filters[commodity]": crop,
        "limit": 5
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "records" in data and data["records"]:
        for r in data["records"]:
            print(f"Market: {r['market']} | Crop: {r['commodity']} | Modal: ₹{r['modal_price']}")
    else:
        print("Response:", data)

get_mandi_price()