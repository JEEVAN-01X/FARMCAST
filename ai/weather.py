import requests

def get_weather(lat=12.97, lon=77.59, location="Bengaluru"):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "Asia/Kolkata",
        "forecast_days": 3
    }
    r = requests.get(url, params=params)
    data = r.json()
    
    print(f"Weather for {location}:")
    for i in range(3):
        print(f"{data['daily']['time'][i]} | Max: {data['daily']['temperature_2m_max'][i]}°C | Rain: {data['daily']['precipitation_sum'][i]}mm")

get_weather()