from datetime import datetime

from packing import create_daily_outfit
from packing import create_packing_list

from weather import get_forecast


def get_date(prompt):
    date_input = input(prompt)

    try:
        return datetime.strptime(date_input, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date. Please enter the date as YYYY-MM-DD")
        raise SystemExit
    

city = input("enter a city: ")
start_date = get_date("Enter the start date of your trip (YYYY-MM-DD): ")
end_date = get_date("Enter the end date of your trip (YYYY-MM-DD): ")

if end_date < start_date:
    print("End date cannot be before start date.")
    raise SystemExit

trip_length = (end_date - start_date).days + 1

forecast = get_forecast(city, start_date, end_date)

print()
daily_outfits = []

for day in forecast:
    outfit = create_daily_outfit(day)
    daily_outfits.append(outfit)
    print(day["date"])
    print("High:", day["high"], "Requirement:", round(day["high_requirement"], 2))
    print("Low:", day["low"], "Requirement:", round(day["low_requirement"], 2))
    print("Rain protection required?:", day["rain_protection"])
    print()

packing_list = create_packing_list(daily_outfits, trip_length)

print(packing_list)

print()