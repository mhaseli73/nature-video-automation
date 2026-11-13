import json
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

def main():
    output_dir = Path("output")
    audio_dir = output_dir / "audio"
    
    # 1. Load the downloaded video assets
    assets_file = output_dir / "video_assets.json"
    if not assets_file.exists():
        raise FileNotFoundError("video_assets.json not found. Run visual_fetcher first.")
        
    with open(assets_file, encoding="utf-8") as f:
        video_paths = json.load(f)

    if not video_paths:
        raise RuntimeError("No video clips were downloaded by the fetcher.")

    # 2. Find all generated audio files (e.g., short_narration.mp3, long_narration.mp3)
    audio_files = list(audio_dir.glob("*_narration.mp3"))
    if not audio_files:
        raise FileNotFoundError("No narration files found in output/audio/")

    for audio_path in audio_files:
        video_type = audio_path.stem.replace("_narration", "")
        print(f"\nRendering {video_type} video...")

        # 3. Load the voiceover audio to get the exact duration
        narration = AudioFileClip(str(audio_path))
        target_duration = narration.duration

        # 4. Build the video by adding clips until we match the audio length
        clips = []
        current_duration = 0.0

        for path in video_paths:
            if current_duration >= target_duration:
                break
            
            clip = VideoFileClip(path)
            remaining_time = target_duration - current_duration
            
            # If adding this whole clip exceeds the audio time, trim the clip
            if clip.duration > remaining_time:
                clip = clip.subclip(0, remaining_time)
            
            clips.append(clip)
            current_duration += clip.duration

        if not clips:
            print(f"Warning: Could not assemble clips for {video_type}. Skipping.")
            continue

        # 5. Combine everything
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.set_audio(narration)
        final_video = final_video.set_duration(target_duration)

        # 6. Export the final video
        output_video_path = output_dir / f"{video_type}_final_video.mp4"
        print(f"Exporting to {output_video_path}...")
        
        final_video.write_videofile(
            str(output_video_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger="bar"
        )
        
        # Close clips to free up memory
        final_video.close()
        for c in clips:
            c.close()
        narration.close()

    print("\nVideo rendering complete!")

if __name__ == "__main__":
    main()
