
import os
import json
import time
from pathlib import Path

from google import genai
from google.genai import types, errors


PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

RETRY_DELAYS = [5, 15, 30]
TEMPORARY_ERRORS = [429, 500, 502, 503, 504]


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    return genai.Client(api_key=api_key)


def generate_with_retry(client, model, prompt):

    for attempt in range(len(RETRY_DELAYS) + 1):

        try:
            print(
                f"Trying {model} "
                f"(attempt {attempt + 1})..."
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.8,
                    max_output_tokens=4000
                )
            )

            if not response.text:
                raise ValueError("Empty Gemini response")

            return json.loads(response.text)

        except errors.APIError as error:

            status = getattr(error, "code", None)

            print(f"Gemini API error: {status} - {error}")

            if status not in TEMPORARY_ERRORS:
                raise

            if attempt < len(RETRY_DELAYS):
                delay = RETRY_DELAYS[attempt]

                print(f"Waiting {delay} seconds...")
                time.sleep(delay)

            else:
                print(f"{model} failed after all retries.")

    return None


def generate_script(plan, research, client):

    video_type = plan["video_type"]

    if video_type == "short":
        target_words = "120 to 140 words"
        duration = "60 seconds"
    else:
        target_words = "480 to 520 words"
        duration = "4 minutes"

    prompt = f"""
You are a professional international travel
documentary writer and YouTube strategist.

Create an original, engaging English travel script.

DESTINATION:
{plan['destination']}, {plan['country']}

MAIN THEME:
{plan.get('theme', '')}

VIDEO CONCEPT:
{plan.get('topic_angle', '')}

TARGET AUDIENCE:
United States, United Kingdom, Europe and Australia.

AUDIENCE INTEREST:
{plan.get('audience_reason', '')}

RESEARCH:
{research.get('description', '')}

RESEARCH SOURCE:
{research.get('source', '')}

VISUAL IDEAS:
{json.dumps(plan.get('visual_ideas', []))}

VIDEO FORMAT:
{video_type}

TARGET DURATION:
{duration}

TARGET SCRIPT LENGTH:
{target_words}

INSTRUCTIONS:

1. Start with a compelling hook.
2. Use natural, fluent spoken English.
3. Make the narration cinematic and engaging.
4. Avoid generic filler and repetitive phrases.
5. Include specific attractions and experiences
   only when supported by reliable information.
6. Never invent prices, opening hours or facts.
7. Do not present unverified information as fact.
8. Make the narration suitable for voice-over.
9. Include visual suggestions for each section.
10. End with a natural audience engagement question.

For SHORT:
Use a fast opening, strong visual moments and
a memorable ending.

For LONG:
Create a structured travel documentary with:
- Introduction
- Main attractions
- Nature and landscapes
- Local culture and experiences
- Practical travel information
- Memorable conclusion

Return ONLY valid JSON:

{{
  "title": "Video title",
  "hook": "Opening hook",
  "narration": "Complete voice-over script",
  "visual_suggestions": [
    "Visual suggestion 1",
    "Visual suggestion 2"
  ],
  "description": "YouTube video description",
  "tags": ["travel", "destination"]
}}
"""

    print(f"Generating {video_type} script...")

    result = generate_with_retry(
        client,
        PRIMARY_MODEL,
        prompt
    )

    if result is None:
        print("Switching to fallback model...")

        result = generate_with_retry(
            client,
            FALLBACK_MODEL,
            prompt
        )

    if result is None:
        raise RuntimeError(
            f"Both Gemini models failed for {video_type} script."
        )

    required = [
        "title",
        "hook",
        "narration",
        "visual_suggestions",
        "description",
        "tags"
    ]

    for field in required:
        if field not in result:
            raise ValueError(
                f"Missing script field: {field}"
            )

    if not all(
        isinstance(result[field], str) and result[field].strip()
        for field in ["title", "hook", "narration", "description"]
    ):
        raise ValueError("Invalid script text fields")

    if not isinstance(result["visual_suggestions"], list):
        raise ValueError("Invalid visual suggestions")

    if not isinstance(result["tags"], list):
        raise ValueError("Invalid tags")

    print(f"{video_type.capitalize()} script generated successfully!")

    return result


def main():

    output = Path("output")
    script_folder = output / "scripts"

    script_folder.mkdir(parents=True, exist_ok=True)

    with open(
        output / "video_plan.json",
        encoding="utf-8"
    ) as file:
        plans = json.load(file)

    with open(
        output / "destination_research.json",
        encoding="utf-8"
    ) as file:
        research = json.load(file)

    client = get_client()

    for plan in plans:

        video_type = plan["video_type"]

        print(f"\nGenerating: {video_type}")

        result = generate_script(
            plan,
            research,
            client
        )

        filename = f"{video_type}_script.json"

        json_path = script_folder / filename

        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        text_file = script_folder / (
            f"{video_type}_script.txt"
        )

        text_file.write_text(
            result["title"]
            + "\n\n"
            + result["narration"],
            encoding="utf-8"
        )

        print(f"Created: {filename}")

    print("\nGemini script generation completed!")


if __name__ == "__main__":
    main()
