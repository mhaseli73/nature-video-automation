import os
import json
import re
import requests
from pathlib import Path
from urllib.parse import quote

def fetch_mixkit_video(query, output_dir):
    """Fetches a direct MP4 link from Mixkit without an API key."""
    # Format the query for the URL (e.g., "lion in savannah" -> "lion-in-savannah")
    search_slug = query.lower().replace(" ", "-")
    search_url = f"https://mixkit.co/free-stock-video/{search_slug}/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        print(f"Searching Mixkit for: {query}")
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()

        # Use regex to find direct MP4 links in the page source
        # Pattern looks for: https://assets.mixkit.co/videos/.../...-720.mp4
        pattern = r'https://assets\.mixkit\.co/videos/[0-9]+/[0-9]+-720\.mp4'
        matches = re.findall(pattern, response.text)

        if not matches:
            print(f"No videos found on Mixkit for: {query}")
            return None

        # Take the first unique link
        video_url = sorted(set(matches))[0]
        print(f"Found video URL: {video_url}")

        # Create a safe filename and download
        safe_query = quote(query, safe="")
        local_filename = output_dir / f"clip_{safe_query}.mp4"

        video_data = requests.get(video_url, headers=headers, timeout=60)
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

    scene_plan_files = list(scene_plans_dir.glob("*_scene_plan.json"))
    if not scene_plan_files:
        raise FileNotFoundError("No scene plan files found in output/scene_plans/")

    all_video_paths = []

    for plan_file in scene_plan_files:
        print(f"Processing scene plan: {plan_file.name}")
        with open(plan_file, encoding="utf-8") as f:
            scene_plan = json.load(f)

        for scene in scene_plan.get("scenes", []):
            # Use the correct key from your scene_planner.py
            query = scene.get("pexels_video_query")
            if query:
                # Switch from Pexels to Mixkit
                path = fetch_mixkit_video(query, clips_dir)
                if path:
                    all_video_paths.append(path)

    # Save the list of downloaded clips for the renderer
    with open(output_dir / "video_assets.json", "w", encoding="utf-8") as f:
        json.dump(all_video_paths, f, indent=4)

    print(f"Downloaded {len(all_video_paths)} video clips total.")

if __name__ == "__main__":
    main()
