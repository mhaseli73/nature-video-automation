import os
import json
import requests
from pathlib import Path
from urllib.parse import quote

def fetch_pexels_video(query, output_dir):
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY is missing")

    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
        "size": "medium"
    }

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("videos"):
            print(f"No video found for query: {query}")
            return None

        video_files = data["videos"][0]["video_files"]
        video_url = video_files[0]["link"]

        safe_query = quote(query, safe="")
        local_filename = output_dir / f"clip_{safe_query}.mp4"

        print(f"Downloading: {video_url}")
        video_data = requests.get(video_url, timeout=60)
        video_data.raise_for_status()

        with open(local_filename, "wb") as f:
            f.write(video_data.content)

        return str(local_filename)

    except requests.RequestException as error:
        print(f"Error fetching video for '{query}': {error}")
        return None

def main():
    output_dir = Path("output")
    scene_plans_dir = output_dir / "scene_plans"
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    # Find all scene plan files (e.g., short_scene_plan.json, long_scene_plan.json)
    scene_plan_files = list(scene_plans_dir.glob("*_scene_plan.json"))
    if not scene_plan_files:
        raise FileNotFoundError("No scene plan files found in output/scene_plans/")

    all_video_paths = []

    for plan_file in scene_plan_files:
        print(f"Processing scene plan: {plan_file.name}")
        with open(plan_file, encoding="utf-8") as f:
            scene_plan = json.load(f)

        for scene in scene_plan.get("scenes", []):
            # Use the correct key from scene_planner.py
            query = scene.get("pexels_video_query")
            if query:
                path = fetch_pexels_video(query, clips_dir)
                if path:
                    all_video_paths.append(path)

    # Save the list of downloaded clips for the renderer
    with open(output_dir / "video_assets.json", "w", encoding="utf-8") as f:
        json.dump(all_video_paths, f, indent=4)

    print(f"Downloaded {len(all_video_paths)} video clips total.")

if __name__ == "__main__":
    main()
