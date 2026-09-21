
from recommendations import calculate_temperature_requirement
from recommendations import needs_rain_protection
import requests

def get_location(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the weather service: {e}")
        raise SystemExit

    data = response.json()

    results = data.get("results")

    if not results:
        print("city not found.")
        raise SystemExit
            
    return data["results"][0]
   


def get_weather(location, start_date, end_date):
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": location['latitude'],
        "longitude": location['longitude'],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "weather_code"
        ],
        "temperature_unit": "fahrenheit",
        "timezone": "auto",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    try:
        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )
        weather_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not retrieve weather data: {e}")
        raise SystemExit

    return weather_response.json()["daily"]

def get_forecast(city, start_date, end_date):
    location = get_location(city)
    daily = get_weather(location, start_date, end_date)
    forecast = []
    for i in range(len(daily["time"])):
        high = daily["temperature_2m_max"][i]
        low = daily["temperature_2m_min"][i]
        rain_protection = needs_rain_protection(daily["precipitation_probability_max"][i])

        high_requirement = calculate_temperature_requirement(high)
        low_requirement = calculate_temperature_requirement(low)

        day = {
            "date": daily["time"][i],
            "high": daily["temperature_2m_max"][i],
            "low": daily["temperature_2m_min"][i],
            "high_requirement": high_requirement,
            "low_requirement": low_requirement,
            "rain_chance": daily["precipitation_probability_max"][i],
            "rain_protection": rain_protection,
            "weather_code": daily["weather_code"][i]

        }

        forecast.append(day)

    return forecast

