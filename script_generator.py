
import json
from pathlib import Path


def load_research():
    path = Path("output/destination_research.json")

    if path.exists():
        with open(path, encoding="utf-8") as file:
            return json.load(file)

    return {}


def generate_short(destination, research):
    name = destination["destination"]
    country = destination["country"]
    description = research.get("description", "")

    if not description:
        description = (
            f"{name} is a destination in {country} "
            "worth exploring."
        )

    return f"""
TITLE: Discover {name}

HOOK:
Looking for your next unforgettable adventure?

INTRODUCTION:
Welcome to {name}, in {country}!

DISCOVER:
{description}

EXPERIENCE:
Explore the scenery, discover local attractions,
and experience the unique character of this destination.

TRAVEL TIP:
Research the best season to visit and plan your trip.

ENDING:
Would you visit {name}?
Follow us for more amazing places around the world!
"""


def generate_long(destination, research):
    name = destination["destination"]
    country = destination["country"]
    description = research.get("description", "")

    if not description:
        description = f"{name} is located in {country}."

    return f"""
TITLE: Exploring {name} | Complete Travel Guide

INTRODUCTION:
Welcome to another travel adventure!
Today, we are exploring {name}, in {country}.

CHAPTER 1 - INTRODUCTION:
{description}

CHAPTER 2 - WHAT TO EXPLORE:
Discover the most interesting attractions,
landscapes and experiences in this destination.

CHAPTER 3 - LOCAL EXPERIENCES:
Explore local culture, food, traditions
and the atmosphere of the region.

CHAPTER 4 - TRAVEL PLANNING:
Research transportation, accommodation,
travel costs and the best visiting season.

CHAPTER 5 - WHY VISIT:
Discover what makes this destination
interesting for international travelers.

CONCLUSION:
Would you add {name} to your travel bucket list?
Subscribe for more travel discoveries!
"""


def main():
    with open("output/video_plan.json", encoding="utf-8") as file:
        plans = json.load(file)

    research = load_research()

    output = Path("output/scripts")
    output.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        if plan["video_type"] == "short":
            script = generate_short(plan, research)
        else:
            script = generate_long(plan, research)

        filename = f'{plan["video_type"]}_script.txt'

        (output / filename).write_text(
            script.strip(),
            encoding="utf-8"
        )

        print("Created:", filename)

    print("Research-based script generation completed!")


if __name__ == "__main__":
    main()
