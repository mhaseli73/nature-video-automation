
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

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.8,
            max_output_tokens=4000
        )
    )

    result = json.loads(response.text)

    for field in [
        "title",
        "hook",
        "narration",
        "visual_suggestions",
        "description",
        "tags"
    ]:
        if field not in result:
            raise ValueError(f"Missing script field: {field}")

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
        print("Generating:", plan["video_type"])

        result = generate_script(plan, research, client)

        filename = f'{plan["video_type"]}_script.json'

        with open(
            script_folder / filename,
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
            f'{plan["video_type"]}_script.txt'
        )

        text_file.write_text(
            result["title"]
            + "\n\n"
            + result["narration"],
            encoding="utf-8"
        )

        print("Created:", filename)

    print("Gemini script generation completed!")


if __name__ == "__main__":
    main()
