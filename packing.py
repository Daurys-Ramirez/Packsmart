from recommendations import choose_accessories
from recommendations import choose_bottoms
from recommendations import choose_tops


def create_daily_outfit(day):
    day_requirement = day["low_requirement"]
    return {
        "date": day["date"],
        "tops": choose_tops(day_requirement),
        "bottoms": choose_bottoms(day_requirement),
        "accessories": choose_accessories(day_requirement),
        "rain_protection": day["rain_protection"]
    }


def create_packing_list(daily_outfits, trip_length):
    packing_list = {}

    # This implimentation could be made shorter with dict.get() - to be explored
    for outfit in daily_outfits:
        for top in outfit["tops"]:
            if top == "heavy jacket":
                packing_list[top] = 1
            elif top in packing_list:
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
            packing_list["umbrella"] = 1

    packing_list["socks"] = trip_length
    packing_list["underwear"] = trip_length

    return packing_list
