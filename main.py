
import json
import random
from pathlib import Path

# Travel video production brain

DESTINATIONS = [
    {
        "name": "Swiss Alps",
        "country": "Switzerland",
        "theme": "mountains and nature"
    },
    {
        "name": "Santorini",
        "country": "Greece",
        "theme": "islands and architecture"
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "theme": "tropical beaches"
    },
    {
        "name": "Dolomites",
        "country": "Italy",
        "theme": "mountains and hiking"
    },
    {
        "name": "Banff National Park",
        "country": "Canada",
        "theme": "lakes and wildlife"
    }
]

def choose_destination():
    return random.choice(DESTINATIONS)

def create_video_plan(destination, video_type):
    return {
        "destination": destination["name"],
        "country": destination["country"],
        "theme": destination["theme"],
        "video_type": video_type,
        "language": "English",
        "audience": "International travelers",
        "status": "planned"
    }

def main():
    destination = choose_destination()

    plans = [
        create_video_plan(destination, "short"),
        create_video_plan(destination, "long")
    ]

    Path("output").mkdir(exist_ok=True)

    with open("output/video_plan.json", "w",
              encoding="utf-8") as file:
        json.dump(plans, file, indent=4)

    print("Travel video plans created!")
    print(json.dumps(plans, indent=4))

if __name__ == "__main__":
    main()
