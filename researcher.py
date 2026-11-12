
import json
import requests
from pathlib import Path
from urllib.parse import quote


def research_destination(destination):
    name = destination["destination"]
    country = destination["country"]

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + quote(name, safe="")
    )

    result = {
        "destination": name,
        "country": country,
        "topic_angle": destination.get("topic_angle", ""),
        "audience_reason": destination.get("audience_reason", ""),
        "visual_ideas": destination.get("visual_ideas", []),
        "theme": destination.get("theme", ""),
        "description": "",
        "source": "",
        "status": "failed"
    }

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "TravelVideoResearchBot/1.0"},
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        result["description"] = data.get("extract", "")
        result["source"] = (
            data.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        )

        if result["description"]:
            result["status"] = "success"

    except requests.RequestException as error:
        result["error"] = str(error)

    return result


def main():
    output = Path("output")
    output.mkdir(exist_ok=True)

    with open(
        output / "video_plan.json",
        encoding="utf-8"
    ) as file:
        plans = json.load(file)

    destination = plans[0]
    result = research_destination(destination)

    with open(
        output / "destination_research.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("Research completed:", result["status"])


if __name__ == "__main__":
    main()
