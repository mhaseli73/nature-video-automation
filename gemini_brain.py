
import os
import json
import time
from pathlib import Path

from google import genai
from google.genai import types, errors


PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

RETRY_DELAYS = [10, 30, 60]

TEMPORARY_ERRORS = [408, 429, 500, 502, 503, 504]


def get_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    return genai.Client(api_key=api_key)


def is_daily_quota_error(error):

    message = str(error).lower()

    indicators = [
        "per day",
        "per_day",
        "daily quota",
        "requests per day",
        "limit exceeded",
        "free tier"
    ]

    return any(item in message for item in indicators)


def generate_with_retry(client, model, prompt):

    for attempt in range(len(RETRY_DELAYS) + 1):

        try:

            print(
                f"Trying {model} "
                f"(attempt {attempt + 1}/"
                f"{len(RETRY_DELAYS) + 1})...",
                flush=True
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.5,
                    max_output_tokens=1500
                )
            )

            if not response.text:
                print("Gemini returned an empty response.")
                return None

            try:

                result = json.loads(response.text)

            except json.JSONDecodeError as error:

                print(
                    f"Invalid JSON from {model}: {error}",
                    flush=True
                )

                print(
                    f"Response preview: {response.text[:500]}",
                    flush=True
                )

                return None

            if not isinstance(result, dict):

                print("Gemini response is not a JSON object.")
                return None

            return result

        except errors.APIError as error:

            status = getattr(error, "code", None)

            print(
                f"Gemini API error: {status} - {error}",
                flush=True
            )

            # Daily quota errors cannot be fixed by short retries.

            if status == 429 and is_daily_quota_error(error):

                print(
                    f"Daily quota exhausted for {model}.",
                    flush=True
                )

                return None

            if status not in TEMPORARY_ERRORS:
                raise

            if attempt < len(RETRY_DELAYS):

                delay = RETRY_DELAYS[attempt]

                print(
                    f"Temporary error. "
                    f"Retrying in {delay} seconds...",
                    flush=True
                )

                time.sleep(delay)

            else:

                print(
                    f"{model} failed after all retries.",
                    flush=True
                )

    return None


def choose_destination():

    history_file = Path("output/decision_history.json")

    history = []

    if history_file.exists():

        try:

            history = json.loads(
                history_file.read_text(encoding="utf-8")
            )

            if not isinstance(history, list):
                history = []

        except (json.JSONDecodeError, OSError):

            history = []

    recent_destinations = [
        item.get("destination")
        for item in history[-20:]
        if isinstance(item, dict)
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
{json.dumps(recent_destinations, ensure_ascii=False)}

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

    print("Trying primary Gemini model...", flush=True)

    result = generate_with_retry(
        client,
        PRIMARY_MODEL,
        prompt
    )

    if result is None:

        print(
            "Primary model unavailable. "
            "Switching to fallback model...",
            flush=True
        )

        result = generate_with_retry(
            client,
            FALLBACK_MODEL,
            prompt
        )

    if result is None:

        raise RuntimeError(
            "Both Gemini models failed. "
            "Check API quota and model availability."
        )

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

        raise ValueError(
            "Invalid destination information"
        )

    if (
        not isinstance(result["visual_ideas"], list)
        or not result["visual_ideas"]
        or not all(
            isinstance(item, str) and item.strip()
            for item in result["visual_ideas"]
        )
    ):

        raise ValueError("Invalid visual ideas")

    print(
        "Destination successfully selected!",
        flush=True
    )

    return result


if __name__ == "__main__":

    destination = choose_destination()

    print(
        json.dumps(
            destination,
            indent=4,
            ensure_ascii=False
        )
    )
