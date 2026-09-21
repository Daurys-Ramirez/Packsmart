from clothing import clothing

def calculate_temperature_requirement(temperature):
    requirement = (temperature - 60) / 3
    requirement = max(-10, min(10, requirement))
    return requirement

def needs_rain_protection(rain_chance):
    return rain_chance >= 60

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