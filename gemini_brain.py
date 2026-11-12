
import os
import json
from pathlib import Path
from google import genai
from google.genai import types

MODEL = "gemini-3.8-flash"

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    return genai.Client(api_key=api_key)


def choose_destination():
    history_file = Path("output/decision_history.json")

    history = []

    if history_file.exists():
        history = json.loads(
            history_file.read_text(encoding="utf-8")
        )

    recent_destinations = [
        item.get("destination")
        for item in history[-20:]
    ]

    prompt = f"""
You are the strategic AI director of an international
travel YouTube channel called Amazing Places Around
the World.

Your target audience:
United States, United Kingdom, Europe and Australia.

Your task:
Choose ONE excellent travel destination for today's
video production.

Consider:
- International tourist interest
- Visual beauty and cinematic potential
- Unique attractions and experiences
- Seasonal relevance
- Variety of destinations and countries
- Potential viewer interest

Avoid recently selected destinations:
{json.dumps(recent_destinations)}

Choose a destination that offers enough interesting
material for both a 60-second Short and a 4-minute
travel documentary.

Return ONLY valid JSON with these fields:

{{
  "name": "Destination name",
  "country": "Country",
  "theme": "Main travel theme",
  "topic_angle": "Unique video concept",
  "audience_reason": "Why international viewers may like it",
  "visual_ideas": [
    "Visual idea 1",
    "Visual idea 2",
    "Visual idea 3"
  ]
}}
"""

    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.8,
            max_output_tokens=1000
        )
    )

    result = json.loads(response.text)

    required = [
        "name",
        "country",
        "theme",
        "topic_angle",
        "audience_reason",
        "visual_ideas"
    ]

    for field in required:
        if field not in result:
            raise ValueError(
                f"Gemini response missing: {field}"
            )

    if not all(
        isinstance(result[field], str)
        and result[field].strip()
        for field in required[:5]
    ):
        raise ValueError("Invalid destination information")

    if not isinstance(result["visual_ideas"], list):
        raise ValueError("Invalid visual ideas")

    return result


if __name__ == "__main__":
    destination = choose_destination()
    print(json.dumps(
        destination,
        indent=4,
        ensure_ascii=False
    ))
