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
        "size": "medium" # Good balance for GitHub Actions
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
        # Pick the first available link (usually HD)
        video_url = video_files[0]["link"]
        
        # Download the video
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
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "scene_plan.json", encoding="utf-8") as f:
        scene_plan = json.load(f)

    video_paths = []
    for scene in scene_plan.get("scenes", []):
        query = scene.get("visual_query")
        if query:
            path = fetch_pexels_video(query, clips_dir)
            if path:
                video_paths.append(path)

    # Save the list of downloaded clips for the renderer
    with open(output_dir / "video_assets.json", "w", encoding="utf-8") as f:
        json.dump(video_paths, f, indent=4)

    print(f"Downloaded {len(video_paths)} video clips.")

if __name__ == "__main__":
    main()
