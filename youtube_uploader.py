import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_client():
    """Authenticates with YouTube using credentials from GitHub Secrets."""
    token_json_str = os.getenv("YT_TOKEN_JSON")
    
    if not token_json_str:
        # Fallback for local testing if you download the token.json file
        if Path("token.json").exists():
            return build("youtube", "v3", credentials=Credentials.from_authorized_user_file("token.json", SCOPES))
        raise RuntimeError("YT_TOKEN_JSON environment variable is missing.")

    # Load credentials from the GitHub Secret string
    creds_info = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file_path, title, description, tags, is_short=False):
    """Uploads a video to YouTube."""
    print(f"Uploading {file_path} to YouTube...")
    
    body = {
        "snippet": {
            "title": title[:100], # YouTube title limit is 100 chars
            "description": description[:5000], # YouTube description limit is 5000 chars
            "tags": tags,
            "categoryId": "19" # 19 = Travel & Events
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # If it's a Short, add #Shorts to the title
    if is_short and "#Shorts" not in body["snippet"]["title"]:
        body["snippet"]["title"] += " #Shorts"

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print(f"✅ Successfully uploaded! Video ID: {response['id']}")
    return response['id']

def main():
    output_dir = Path("output")
    
    # Load the video plan to get the title and details
    plan_file = output_dir / "video_plan.json"
    if not plan_file.exists():
        raise FileNotFoundError("video_plan.json not found.")
        
    with open(plan_file, encoding="utf-8") as f:
        plans = json.load(f)
        
    # Extract metadata from the first plan
    destination = plans[0]["destination"]
    topic_angle = plans[0]["topic_angle"]
    
    title = f"{destination}: {topic_angle}"
    description = f"Explore the beautiful {destination} in this cinematic travel documentary.\n\n{topic_angle}\n\n#travel #{destination.replace(' ', '')} #documentary"
    tags = ["travel", destination, "nature documentary", "cinematic", "amazing places"]

    youtube = get_youtube_client()

    # Upload the long video
    long_video = output_dir / "long_final_video.mp4"
    if long_video.exists():
        upload_video(youtube, str(long_video), title, description, tags, is_short=False)
    else:
        print("⚠️ long_final_video.mp4 not found.")

    # Upload the short video
    short_video = output_dir / "short_final_video.mp4"
    if short_video.exists():
        upload_video(youtube, str(short_video), title, description, tags, is_short=True)
    else:
        print("⚠️ short_final_video.mp4 not found.")

if __name__ == "__main__":
    main()
