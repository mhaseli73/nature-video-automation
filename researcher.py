
import json
import requests
from pathlib import Path
from urllib.parse import quote


def research_destination(destination):
    name = destination["destination"]

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + quote(name, safe="")
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "TravelVideoResearchBot/1.0"},
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        return {
            "destination": name,
            "country": destination["country"],
            "description": data.get("extract", ""),
            "source": data.get("content_urls", {})
                .get("desktop", {}).get("page", ""),
            "status": "success"
        }

    except requests.RequestException as error:
        return {
            "destination": name,
            "country": destination["country"],
            "description": "",
            "status": "failed",
            "error": str(error)
        }


def main():
    with open("output/video_plan.json", encoding="utf-8") as file:
        plans = json.load(file)

    destination = plans[0]
    result = research_destination(destination)

    Path("output").mkdir(exist_ok=True)

    with open(
        "output/destination_research.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("Research completed:", result["status"])


if __name__ == "__main__":
    main()
