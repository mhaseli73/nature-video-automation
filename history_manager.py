import json
from pathlib import Path

HISTORY_FILE = Path("output/history.json")

def load_history():
    """Loads the history of past videos."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"past_topics": []}

def save_topic(topic):
    """Saves a new topic to the history file."""
    history = load_history()
    if topic not in history["past_topics"]:
        history["past_topics"].append(topic)
        
    # Keep the history file from getting too large (optional, keeps last 50)
    if len(history["past_topics"]) > 50:
        history["past_topics"] = history["past_topics"][-50:]
        
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def get_avoidance_text():
    """Creates a string for the prompt to tell Gemini what to avoid."""
    history = load_history()
    if not history["past_topics"]:
        return "No previous topics."
    
    # Join the past topics into a readable list
    return ", ".join(history["past_topics"])
