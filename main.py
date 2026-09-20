import requests
from datetime import datetime

def calculate_temperature_requirement(temperature):
    requirement = (temperature - 60) / 3
    requirement = max(-10, min(10, requirement))
    return requirement

def needs_rain_protection(rain_chance):
    return rain_chance >= 60

clothing = {
    "bottoms": [
        {"name": "shorts", "resistance": -4.0, "layerable": False},
        {"name": "jeans", "resistance": 1.0, "layerable": False},
        {"name": "sweatpants", "resistance": 2.5, "layerable": False}
    ],

    "tops": [
        # inner to outer
        {"name": "t-shirt", "resistance": -2.0, "layerable": True},
        {"name": "long-sleeve shirt", "resistance": 1.5, "layerable": True},
        {"name": "sweater", "resistance": 3.0, "layerable": True},
        {"name": "light jacket", "resistance": 3.5, "layerable": False},
        {"name": "heavy jacket", "resistance": 5.5, "layerable": False}
    ],

    "accessories": [
        {"name": "socks", "resistance": 0.0, "layerable": False},
        {"name": "underwear", "resistance": 0.0, "layerable": False}
    ]
}

def choose_bottoms(weather_requirement):
    bottoms = clothing["bottoms"]
    best_item = None
    best_remaining_difference = float("inf")

    for item in bottoms:
        difference = abs(weather_requirement + item["resistance"])

        if difference < best_remaining_difference:
            best_remaining_difference = difference
            best_item = item

    return best_item["name"]

# This function allows for the combination tshirt + heavy Jacket. when temp is around 49 degrees. Heavy Jacket should be reserved for colder temperatures
def choose_tops(weather_requirement):
    tops = clothing["tops"]

    best_combination = []
    best_difference = float("inf")

    def search(start_index, selected, total_resistance):
        nonlocal best_combination, best_difference

        # Evaluate the current combination
        if selected:
            difference = abs(weather_requirement + total_resistance)

            if difference < best_difference:
                best_difference = difference
                best_combination = selected.copy()

        # Try adding another layer
        for i in range(start_index, len(tops)):
            item = tops[i]

            # Cannot place another item over a non-layerable item
            if selected and not selected[-1]["layerable"]:
                break

            selected.append(item)

            search(
                i + 1,
                selected,
                total_resistance + item["resistance"]
            )

            selected.pop()

    search(0, [], 0)

    return [item["name"] for item in best_combination]

def choose_accessories(weather_requirement):
    accessories = []
    if weather_requirement <= -8.0:
        accessories.extend(["gloves", "hat"])
    return accessories

def create_daily_outfit(day):
    day_requirement = day["low_requirement"]
    return {
        "date": day["date"],
        "tops": choose_tops(day_requirement),
        "bottoms": choose_bottoms(day_requirement),
        "accessoires": choose_accessories(day_requirement),
        "rain_protection": day["rain_protection"]
    }


def create_packing_list(daily_outfits):
    packing_list = {}

    # This implimentation could be made shorter with dict.get() - to be explored
    for outfit in daily_outfits:
        for top in outfit["tops"]:
            if top in packing_list:
                packing_list[top] += 1
            else:
                packing_list[top] = 1

        for accessory in outfit["accessories"]:
            packing_list[accessory] = 1

        bottom = outfit["bottoms"]

        if bottom in packing_list:
            packing_list[bottom] += 1
        else: 
            packing_list[bottom] = 1

        if outfit["rain_protection"]:
            packing_list["umbrella"]


    return packing_list

city = input("enter a city: ")
start_date = datetime.strptime(input("Enter the start date of your trip (YYYY-MM-DD): "), "%Y-%m-%d").date()
end_date = datetime.strptime(input("Enter the end date of your trip (YYYY-MM-DD): "), "%Y-%m-%d").date()

if end_date < start_date:
    print("End date cannot be before start date.")
    raise SystemExit

trip_length = (end_date - start_date).days + 1

print(f"trip length: {trip_length} days")

url = "https://geocoding-api.open-meteo.com/v1/search"

params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
}

response = requests.get(url, params=params)

print(response.url)

data = response.json()



results = data.get("results")

if not results:
    print("city not found.")
    raise SystemExit
   
    
location = data["results"][0]


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

weather_response = requests.get(weather_url, params=weather_params)

weather_data = weather_response.json()

daily = weather_data["daily"]

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

print()
daily_outfits = []

for day in forecast:
    outfit = create_daily_outfit(day)
    daily_outfits.append(outfit)
    print(day["date"])
    print("High:", day["high"], "Requirement:", round(day["high_requirement"], 2))
    print("Low:", day["low"], "Requirement:", round(day["low_requirement"], 2))
    print("Rain protection required?:", day["rain_protection"])
    # print(create_daily_outfit(day))
    print()

packing_list = create_packing_list(daily_outfits)
packing_list["socks"] = trip_length
packing_list["underwear"] = trip_length
print(packing_list)

print(f"City: {location['name']}")
print(f"Latitude: {location['latitude']}")
print(f"Longitude: {location['longitude']}")
print(f"Timezone: {location['timezone']}")

print()