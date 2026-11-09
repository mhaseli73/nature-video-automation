
import json
from pathlib import Path


def generate_short(destination):
    name = destination["destination"]
    country = destination["country"]
    theme = destination["theme"]

    return f"""
TITLE: Discover {name}

HOOK:
What if your next unforgettable adventure
was waiting for you in {name}?

INTRODUCTION:
Welcome to {name}, in {country}.

EXPERIENCE:
Explore its {theme}, enjoy the scenery,
and discover what makes this destination special.

TRAVEL TIP:
Research the best season to visit and
plan enough time to explore.

ENDING:
Would you add {name} to your travel bucket list?
Subscribe for more amazing destinations!
"""


def generate_long(destination):
    name = destination["destination"]
    country = destination["country"]
    theme = destination["theme"]

    return f"""
TITLE: Exploring {name} - A Travel Guide

INTRODUCTION:
Imagine discovering a remarkable destination.
Today, we are exploring {name}, in {country}.

SECTION 1 - DISCOVER THE DESTINATION:
Explore the landscape, atmosphere and
character of this destination.

SECTION 2 - WHAT TO EXPERIENCE:
Discover its {theme} and the experiences
travelers can enjoy.

SECTION 3 - TRAVEL PLANNING:
Research transportation, accommodation,
local conditions and the best time to visit.

SECTION 4 - WHY VISIT:
Discover what makes {name} worth considering
for your next adventure.

CONCLUSION:
Would you visit {name}?
Subscribe for more travel discoveries!
"""


def main():
    plan_file = Path("output/video_plan.json")

    if not plan_file.exists():
        print("Video plan not found!")
        return

    with open(plan_file, encoding="utf-8") as file:
        plans = json.load(file)

    output = Path("output/scripts")
    output.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        if plan["video_type"] == "short":
            script = generate_short(plan)
        else:
            script = generate_long(plan)

        filename = f'{plan["video_type"]}_script.txt'

        (output / filename).write_text(
            script.strip(),
            encoding="utf-8"
        )

        print(f"Created: {filename}")


if __name__ == "__main__":
    main()
