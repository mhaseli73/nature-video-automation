
import json
from pathlib import Path
from datetime import datetime, timezone

from gemini_brain import choose_destination


def main():
    output = Path("output")
    output.mkdir(exist_ok=True)

    print("Gemini AI is selecting today's destination...")

    destination = choose_destination()

    print("Selected:", destination["name"], destination["country"])

    plans = [
        {
            "destination": destination["name"],
            "country": destination["country"],
            "theme": destination["theme"],
            "topic_angle": destination["topic_angle"],
            "audience_reason": destination["audience_reason"],
            "visual_ideas": destination["visual_ideas"],
            "video_type": "short",
            "duration": 60,
            "language": "English",
            "audience": "International travelers",
            "status": "planned"
        },
        {
            "destination": destination["name"],
            "country": destination["country"],
            "theme": destination["theme"],
            "topic_angle": destination["topic_angle"],
            "audience_reason": destination["audience_reason"],
            "visual_ideas": destination["visual_ideas"],
            "video_type": "long",
            "duration": 240,
            "language": "English",
            "audience": "International travelers",
            "status": "planned"
        }
    ]

    with open(
        output / "video_plan.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            plans,
            file,
            indent=4,
            ensure_ascii=False
        )

    history_file = output / "decision_history.json"

    history = []

    if history_file.exists():
        try:
            history = json.loads(
                history_file.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            history = []

    history.append({
        "destination": destination["name"],
        "country": destination["country"],
        "topic_angle": destination["topic_angle"],
        "date": datetime.now(timezone.utc).isoformat()
    })

    history = history[-100:]

    history_file.write_text(
        json.dumps(history, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("AI video plans created successfully!")
    print(json.dumps(plans, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
